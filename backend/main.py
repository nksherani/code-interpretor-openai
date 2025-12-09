from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import json
from typing import Optional, List
from pathlib import Path
import shutil
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file first
load_dotenv()

from database import connect_to_mongo, close_mongo_connection, get_database
from assistant_manager import get_openai_client
from token_counter import estimate_file_tokens
from conversation_client import ResponsesClient

# Code interpreter container image (can be overridden via env)
CODE_INTERPRETER_IMAGE = os.getenv("CODE_INTERPRETER_IMAGE", "openai/code-interpreter")

# Global client for responses API
responses_client: ResponsesClient | None = None


def require_responses_client() -> ResponsesClient:
    if responses_client is None:
        raise RuntimeError("Responses client is not initialized")
    return responses_client


def build_code_interpreter_tool():
    """Build code interpreter tool spec per Responses API requirements."""
    return {
        "type": "code_interpreter",
        "container": {"type": "auto", "memory_limit": "4g"}
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global responses_client
    
    # Startup
    print("🚀 Starting application...")
    await connect_to_mongo()
    # Initialize OpenAI client and responses wrapper
    responses_client = ResponsesClient(get_openai_client())
    print(f"✓ Application ready with Responses + Conversations")
    
    yield
    
    # Shutdown
    print("👋 Shutting down application...")
    await close_mongo_connection()

app = FastAPI(
    title="OpenAI Code Interpreter Explorer",
    lifespan=lifespan
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions and log them"""
    logger.error(f"❌ Global exception handler caught: {exc}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc() if os.getenv("DEBUG") else None
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get OpenAI client
client = get_openai_client()

# Store for uploaded files and generated files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Models
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    use_code_interpreter: bool = True

class AnalysisRequest(BaseModel):
    prompt: str
    file_ids: List[str] = []
    thread_id: Optional[str] = None

class ThreadResponse(BaseModel):
    thread_id: str
    message: str
    files: List[dict] = []
    annotations: List[dict] = []

def process_message_content(content):
    """Process message content and extract text and file annotations"""
    text_content = ""
    annotations = []
    
    for item in content:
        if item.type == "text":
            text_content += item.text.value
            # Process annotations
            for annotation in item.text.annotations:
                if annotation.type == "file_path":
                    file_id = annotation.file_path.file_id
                    # Try to get file info to determine if it's an image
                    try:
                        file_info = client.files.retrieve(file_id)
                        filename = file_info.filename if hasattr(file_info, 'filename') else ""
                        # Check if file is an image based on extension
                        is_image = any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'])
                        annotations.append({
                            "type": "image_file" if is_image else "file_path",
                            "file_id": file_id,
                            "text": annotation.text,
                            "filename": filename
                        })
                    except:
                        # If we can't get file info, assume it's a file_path
                        annotations.append({
                            "type": "file_path",
                            "file_id": file_id,
                            "text": annotation.text
                        })
        elif item.type == "image_file":
            annotations.append({
                "type": "image_file",
                "file_id": item.image_file.file_id
            })
    
    return text_content, annotations

# Endpoints
@app.get("/")
async def root():
    return {"message": "OpenAI Code Interpreter Explorer API"}

@app.post("/api/thread/create")
async def create_thread():
    """Create a new conversation (thread)"""
    try:
        rc = require_responses_client()
        convo_id = rc.create_conversation()
        return {"thread_id": convo_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ThreadResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response using Code Interpreter"""
    try:
        logger.info(f"💬 Chat request received: {request.message[:50]}...")
        logger.info(f"Thread ID: {request.thread_id}")
        rc = require_responses_client()
        # Create or reuse conversation
        if request.thread_id:
            conversation_id = request.thread_id
            logger.info(f"Using existing conversation: {conversation_id}")
        else:
            conversation_id = rc.create_conversation()
            logger.info(f"Created new conversation: {conversation_id}")

        # Build input blocks
        input_blocks = [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": request.message}
                ]
            }
        ]

        # Run response with code interpreter if requested (Responses API now requires container)
        tools = []
        if request.use_code_interpreter:
            tools = [build_code_interpreter_tool()]
        logger.info(f"Using tools: {tools}")
        response = rc.run_response(
            conversation_id=conversation_id,
            input_blocks=input_blocks,
            tools=tools,
        )
        response = rc.wait_on_response(response)

        if response.status != "completed":
            error_details = getattr(response, "error", "Unknown error")
            logger.error(f"❌ Response failed: {error_details}")
            raise HTTPException(status_code=500, detail=f"Response failed: {error_details}")

        # Parse response output
        text_content, annotations = rc.parse_response_output(response)
        files = []
        for annotation in annotations:
            if annotation["type"] in ["file_path", "image_file"]:
                files.append({
                    "file_id": annotation["file_id"],
                    "type": annotation["type"],
                    "filename": annotation.get("filename", ""),
                })

        logger.info(f"✓ Chat completed with {len(files)} generated files")

        return ThreadResponse(
            thread_id=conversation_id,
            message=text_content,
            files=files,
            annotations=annotations
        )
    
    except HTTPException as he:
        logger.error(f"❌ HTTP Exception in chat: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in chat endpoint:")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to OpenAI for use with Code Interpreter"""
    try:
        logger.info(f"📤 Upload request received: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        
        # Estimate tokens before upload
        token_info = estimate_file_tokens(file_content, file.filename)
        logger.info(f"📊 Token estimate: {token_info['tokens']} tokens ({token_info['size_kb']} KB)")
        
        # Save file temporarily
        temp_path = UPLOAD_DIR / file.filename
        with open(temp_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Upload to OpenAI
        with open(temp_path, "rb") as f:
            openai_file = client.files.create(
                file=f,
                purpose="input"
            )
        
        logger.info(f"✓ File uploaded successfully: {file.filename} -> {openai_file.id}")
        return {
            "file_id": openai_file.id,
            "filename": file.filename,
            "status": "uploaded",
            "token_estimate": token_info["tokens"],
            "size_kb": token_info["size_kb"],
            "size_bytes": token_info["size_bytes"]
        }
    
    except Exception as e:
        logger.error(f"❌ Error uploading file {file.filename}:")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/analyze")
async def analyze_data(request: AnalysisRequest):
    """Perform data analysis with optional file attachments"""
    try:
        logger.info(f"📊 Analysis request received")
        logger.info(f"Prompt: {request.prompt[:100]}...")
        logger.info(f"Files: {len(request.file_ids)} files")
        rc = require_responses_client()

        # Create conversation
        conversation_id = rc.create_conversation()

        # Build input blocks with text + input_file entries
        content_items = [{"type": "input_text", "text": request.prompt}]
        for file_id in request.file_ids:
            content_items.append({"type": "input_file", "file_id": file_id})

        input_blocks = [
            {
                "role": "user",
                "content": content_items
            }
        ]

        # Run with Code Interpreter (Responses API requires container spec)
        tools = [build_code_interpreter_tool()]
        logger.info(f"Using tools: {tools}")
        response = rc.run_response(
            conversation_id=conversation_id,
            input_blocks=input_blocks,
            tools=tools,
        )
        response = rc.wait_on_response(response)

        if response.status != "completed":
            error_details = getattr(response, "error", "Unknown error")
            logger.error(f"❌ Analysis run failed: {error_details}")

            error_msg = str(error_details)
            if "rate_limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please wait a moment and try again."
                )
            raise HTTPException(status_code=500, detail=f"Analysis failed: {error_details}")

        # Parse response
        text_content, annotations = rc.parse_response_output(response)

        files = []
        for annotation in annotations:
            if annotation["type"] in ["file_path", "image_file"]:
                files.append({
                    "file_id": annotation["file_id"],
                    "type": annotation["type"],
                    "filename": annotation.get("filename", ""),
                })

        logger.info(f"✓ Analysis completed successfully with {len(files)} generated files")
        return ThreadResponse(
            thread_id=conversation_id,
            message=text_content,
            files=files,
            annotations=annotations
        )

    except Exception as e:
        logger.error(f"❌ Error in analyze_data:")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/thread/{thread_id}/messages")
async def get_thread_messages(thread_id: str):
    """Get all messages from a thread"""
    try:
        # Conversations API does not expose message listing the same way as Assistants.
        # For now, return a 501 to indicate not supported in this implementation.
        raise HTTPException(
            status_code=501,
            detail="Listing conversation messages is not supported with Responses/Conversations API in this implementation."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/examples/data-analysis")
async def example_data_analysis():
    """Example: Generate and analyze sample data"""
    prompt = """
    Generate a sample dataset of 100 sales records with columns: date, product, quantity, price, region.
    Then perform the following analysis:
    1. Calculate total revenue by product
    2. Find the best performing region
    3. Create a visualization showing sales trends over time
    4. Calculate summary statistics
    """
    
    request = AnalysisRequest(prompt=prompt)
    return await analyze_data(request)

@app.post("/api/examples/math-computation")
async def example_math():
    """Example: Complex mathematical computation"""
    prompt = """
    Perform the following mathematical computations:
    1. Calculate the first 20 Fibonacci numbers
    2. Find all prime numbers between 1 and 100
    3. Solve the equation: x^3 - 6x^2 + 11x - 6 = 0
    4. Create a plot showing the relationship between x and y where y = sin(x) * e^(-x/10) for x from 0 to 20
    """
    
    request = AnalysisRequest(prompt=prompt)
    return await analyze_data(request)

@app.post("/api/examples/image-generation")
async def example_image():
    """Example: Generate visualizations"""
    prompt = """
    Create the following visualizations:
    1. A heatmap showing correlation between random variables
    2. A 3D surface plot of z = sin(sqrt(x^2 + y^2))
    3. A pie chart showing distribution of fictional market shares
    Save each as a separate image.
    """
    
    request = AnalysisRequest(prompt=prompt)
    return await analyze_data(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

