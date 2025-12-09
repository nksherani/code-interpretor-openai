from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import time
from typing import Optional, List
import tempfile
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
from assistant_manager import get_or_create_assistant, get_openai_client
from token_counter import estimate_file_tokens

# Global variable to store assistant ID
ASSISTANT_ID = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ASSISTANT_ID
    
    # Startup
    print("🚀 Starting application...")
    await connect_to_mongo()
    ASSISTANT_ID = await get_or_create_assistant()
    print(f"✓ Application ready with assistant: {ASSISTANT_ID}")
    
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

# Helper functions
def wait_on_run(run, thread_id):
    """Wait for a run to complete"""
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

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
    """Create a new conversation thread"""
    try:
        thread = client.beta.threads.create()
        return {"thread_id": thread.id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ThreadResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response using Code Interpreter"""
    try:
        logger.info(f"💬 Chat request received: {request.message[:50]}...")
        logger.info(f"Thread ID: {request.thread_id}")
        # Create or use existing thread
        if request.thread_id:
            thread_id = request.thread_id
            logger.info(f"Using existing thread: {thread_id}")
        else:
            thread = client.beta.threads.create()
            thread_id = thread.id
            logger.info(f"Created new thread: {thread_id}")
        
        # Add message to thread
        logger.info(f"Adding message to thread...")
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.message
        )
        logger.info(f"✓ Message added to thread")
        
        # Create and run assistant
        tools = [{"type": "code_interpreter"}] if request.use_code_interpreter else []
        
        logger.info(f"Creating run with assistant: {ASSISTANT_ID}")
        logger.info(f"Tools enabled: {tools}")
        
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            tools=tools
        )
        logger.info(f"✓ Run created: {run.id}, Status: {run.status}")
        
        # Wait for completion
        logger.info(f"Waiting for run to complete...")
        run = wait_on_run(run, thread_id)
        logger.info(f"✓ Run completed with status: {run.status}")
        
        if run.status == "failed":
            error_details = run.last_error if hasattr(run, 'last_error') else 'Unknown error'
            logger.error(f"❌ Run failed with error: {error_details}")
            logger.error(f"Run ID: {run.id}")
            logger.error(f"Thread ID: {thread_id}")
            logger.error(f"Assistant ID: {ASSISTANT_ID}")
            
            # Provide helpful error message
            if hasattr(run.last_error, 'code') and run.last_error.code == 'server_error':
                error_msg = (
                    "OpenAI server error occurred. This might be due to:\n"
                    "1. OpenAI service issues - Check https://status.openai.com/\n"
                    "2. Assistant model compatibility - Try recreating the assistant\n"
                    "3. Temporary API issue - Please try again in a moment\n\n"
                    f"Details: {error_details}"
                )
            else:
                error_msg = f"Run failed: {error_details}"
            
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Get messages
        logger.info(f"Retrieving messages from thread...")
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        latest_message = messages.data[0]
        logger.info(f"✓ Retrieved {len(messages.data)} messages")
        
        # Process content
        logger.info(f"Processing message content...")
        text_content, annotations = process_message_content(latest_message.content)
        logger.info(f"✓ Processed content: {len(text_content)} chars, {len(annotations)} annotations")
        
        # Process file annotations
        files = []
        for annotation in annotations:
            if annotation["type"] in ["file_path", "image_file"]:
                file_id = annotation["file_id"]
                files.append({
                    "file_id": file_id,
                    "type": annotation["type"],
                    "filename": annotation.get("filename", "")
                })
        
        logger.info(f"✓ Processed {len(files)} files: {files}")
        
        response = ThreadResponse(
            thread_id=thread_id,
            message=text_content,
            files=files,
            annotations=annotations
        )
        logger.info(f"✓ Chat response prepared successfully")
        return response
    
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
                purpose="assistants"
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

@app.get("/api/file/{file_id}")
async def download_file(file_id: str):
    """Download or display a file generated by Code Interpreter"""
    try:
        logger.info(f"📥 File request: {file_id}")
        
        # Retrieve file content from OpenAI
        file_data = client.files.content(file_id)
        file_info = client.files.retrieve(file_id)
        
        logger.info(f"✓ Retrieved file: {file_info.filename if hasattr(file_info, 'filename') else 'unknown'}")
        
        # Determine content type based on file extension or default to PNG
        content_type = "image/png"
        filename = f"output_{file_id}.png"
        
        if hasattr(file_info, 'filename') and file_info.filename:
            filename = file_info.filename
            if filename.endswith('.jpg') or filename.endswith('.jpeg'):
                content_type = "image/jpeg"
            elif filename.endswith('.png'):
                content_type = "image/png"
            elif filename.endswith('.gif'):
                content_type = "image/gif"
            elif filename.endswith('.svg'):
                content_type = "image/svg+xml"
            elif filename.endswith('.csv'):
                content_type = "text/csv"
            elif filename.endswith('.json'):
                content_type = "application/json"
            else:
                content_type = "application/octet-stream"
        
        # Return file directly for inline display (images) or download (others)
        return StreamingResponse(
            iter([file_data.content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Cache-Control": "public, max-age=3600"
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Error retrieving file {file_id}:")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"File retrieval failed: {str(e)}")

@app.post("/api/analyze")
async def analyze_data(request: AnalysisRequest):
    """Perform data analysis with optional file attachments"""
    try:
        logger.info(f"📊 Analysis request received")
        logger.info(f"Prompt: {request.prompt[:100]}...")
        logger.info(f"Files: {len(request.file_ids)} files")
        
        # Create thread
        thread = client.beta.threads.create()
        thread_id = thread.id
        
        # Prepare message with file attachments
        attachments = []
        for file_id in request.file_ids:
            attachments.append({
                "file_id": file_id,
                "tools": [{"type": "code_interpreter"}]
            })
        
        # Add message
        logger.info(f"Creating message with {len(attachments)} attachments...")
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.prompt,
            attachments=attachments if attachments else None
        )
        logger.info(f"✓ Message created: {message.id}")
        
        # Run with Code Interpreter
        logger.info(f"Creating run with assistant {ASSISTANT_ID}...")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            tools=[{"type": "code_interpreter"}]
        )
        logger.info(f"✓ Run created: {run.id}, Status: {run.status}")
        
        # Wait for completion
        logger.info(f"Waiting for run to complete...")
        run = wait_on_run(run, thread_id)
        logger.info(f"✓ Run completed with status: {run.status}")
        
        # Check if run failed
        if run.status == "failed":
            error_details = run.last_error if hasattr(run, 'last_error') else 'Unknown error'
            logger.error(f"❌ Analysis run failed: {error_details}")
            
            # Provide user-friendly error message
            error_msg = str(error_details)
            if 'rate_limit' in error_msg.lower():
                raise HTTPException(
                    status_code=429, 
                    detail="Rate limit exceeded. Please wait a moment and try again."
                )
            raise HTTPException(status_code=500, detail=f"Analysis failed: {error_details}")
        
        # Get response
        logger.info(f"Retrieving messages...")
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        logger.info(f"✓ Retrieved {len(messages.data)} messages")
        
        # Get the assistant's response (should be first in list after user message)
        latest_message = messages.data[0]
        logger.info(f"Latest message role: {latest_message.role}")
        
        # Make sure we got the assistant's response, not the user's
        if latest_message.role != "assistant":
            logger.error(f"❌ Expected assistant message, got: {latest_message.role}")
            raise HTTPException(status_code=500, detail="No response from assistant")
        
        text_content, annotations = process_message_content(latest_message.content)
        
        files = []
        for annotation in annotations:
            if annotation["type"] in ["file_path", "image_file"]:
                files.append({
                    "file_id": annotation["file_id"],
                    "type": annotation["type"],
                    "filename": annotation.get("filename", "")
                })
        
        logger.info(f"✓ Analysis completed successfully with {len(files)} generated files")
        return ThreadResponse(
            thread_id=thread_id,
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
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        
        processed_messages = []
        for msg in messages.data:
            text_content, annotations = process_message_content(msg.content)
            processed_messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": text_content,
                "annotations": annotations,
                "created_at": msg.created_at
            })
        
        return {"messages": processed_messages}
    
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

