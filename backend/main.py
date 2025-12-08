from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import time
from typing import Optional, List
import tempfile
from pathlib import Path
import shutil

app = FastAPI(title="OpenAI Code Interpreter Explorer")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
                    annotations.append({
                        "type": "file_path",
                        "file_id": annotation.file_path.file_id,
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
        # Create or use existing thread
        if request.thread_id:
            thread_id = request.thread_id
        else:
            thread = client.beta.threads.create()
            thread_id = thread.id
        
        # Add message to thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.message
        )
        
        # Create and run assistant
        tools = [{"type": "code_interpreter"}] if request.use_code_interpreter else []
        
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
            tools=tools
        )
        
        # Wait for completion
        run = wait_on_run(run, thread_id)
        
        if run.status == "failed":
            raise HTTPException(status_code=500, detail="Run failed")
        
        # Get messages
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        latest_message = messages.data[0]
        
        # Process content
        text_content, annotations = process_message_content(latest_message.content)
        
        # Process file annotations
        files = []
        for annotation in annotations:
            if annotation["type"] == "file_path" or annotation["type"] == "image_file":
                file_id = annotation["file_id"]
                files.append({
                    "file_id": file_id,
                    "type": annotation["type"]
                })
        
        return ThreadResponse(
            thread_id=thread_id,
            message=text_content,
            files=files,
            annotations=annotations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to OpenAI for use with Code Interpreter"""
    try:
        # Save file temporarily
        temp_path = UPLOAD_DIR / file.filename
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to OpenAI
        with open(temp_path, "rb") as f:
            openai_file = client.files.create(
                file=f,
                purpose="assistants"
            )
        
        return {
            "file_id": openai_file.id,
            "filename": file.filename,
            "status": "uploaded"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file/{file_id}")
async def download_file(file_id: str):
    """Download a file generated by Code Interpreter"""
    try:
        # Retrieve file content from OpenAI
        file_data = client.files.content(file_id)
        file_info = client.files.retrieve(file_id)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_file.write(file_data.content)
        temp_file.close()
        
        return FileResponse(
            temp_file.name,
            media_type="application/octet-stream",
            filename=f"output_{file_id}.png"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_data(request: AnalysisRequest):
    """Perform data analysis with optional file attachments"""
    try:
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
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.prompt,
            attachments=attachments if attachments else None
        )
        
        # Run with Code Interpreter
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
            tools=[{"type": "code_interpreter"}]
        )
        
        # Wait for completion
        run = wait_on_run(run, thread_id)
        
        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        latest_message = messages.data[0]
        
        text_content, annotations = process_message_content(latest_message.content)
        
        files = []
        for annotation in annotations:
            if annotation["type"] in ["file_path", "image_file"]:
                files.append({
                    "file_id": annotation["file_id"],
                    "type": annotation["type"]
                })
        
        return ThreadResponse(
            thread_id=thread_id,
            message=text_content,
            files=files,
            annotations=annotations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

