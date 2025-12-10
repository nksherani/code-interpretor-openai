"""
Assistant management - creates and manages OpenAI Assistant
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
from database import get_app_config, set_app_config

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_or_create_assistant() -> str:
    """
    Get existing assistant from DB or create a new one.
    Returns the assistant ID.
    """
    # Try to get existing assistant ID from database
    assistant_id = await get_app_config("assistant_id")
    
    if assistant_id:
        # Verify the assistant still exists in OpenAI
        try:
            client.beta.assistants.retrieve(assistant_id)
            print(f"✓ Using existing assistant: {assistant_id}")
            return assistant_id
        except Exception as e:
            print(f"⚠ Existing assistant not found in OpenAI, creating new one...")
    
    # Create new assistant
    # Using gpt-4.1 which is more stable and cheaper
    assistant = client.beta.assistants.create(
        name="Code Interpreter Explorer",
        instructions="""You are a helpful AI assistant with access to a Python code interpreter. 
        You can analyze data, create visualizations, perform mathematical computations, and work with files.
        Always explain your process and provide clear, detailed responses.
        When creating visualizations, save them as files so users can download them.""",
        model="gpt-4.1",
        tools=[{"type": "code_interpreter"}]
    )
    
    # Save to database
    await set_app_config("assistant_id", assistant.id)
    print(f"✓ Created new assistant: {assistant.id}")
    
    return assistant.id

def get_openai_client():
    """Get OpenAI client instance"""
    return client

