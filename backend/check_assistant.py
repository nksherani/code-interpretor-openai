"""
Script to check and debug assistant configuration
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
from database import connect_to_mongo, get_app_config
import asyncio

load_dotenv()

async def check_assistant():
    """Check if assistant exists and is properly configured"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Connect to MongoDB and get assistant ID
    await connect_to_mongo()
    assistant_id = await get_app_config("assistant_id")
    
    if not assistant_id:
        print("❌ No assistant ID found in database")
        return
    
    print(f"✓ Assistant ID from database: {assistant_id}")
    print()
    
    try:
        # Retrieve assistant
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        print("✓ Assistant found in OpenAI!")
        print(f"  Name: {assistant.name}")
        print(f"  Model: {assistant.model}")
        print(f"  Tools: {assistant.tools}")
        print(f"  Instructions length: {len(assistant.instructions)} chars")
        print(f"  Created at: {assistant.created_at}")
        print()
        
        # Check if model is available
        if assistant.model not in ["gpt-4.1"]:
            print(f"⚠ Warning: Model '{assistant.model}' might not be available")
            print("  Consider updating to: gpt-4.1")
        
        # Check tools
        has_code_interpreter = any(tool.type == "code_interpreter" for tool in assistant.tools)
        if not has_code_interpreter:
            print("❌ Code Interpreter tool is NOT enabled!")
        else:
            print("✓ Code Interpreter is enabled")
        
        print()
        print("Suggestions:")
        print("1. Try using a different model (gpt-4.1)")
        print("2. Check OpenAI status: https://status.openai.com/")
        print("3. Try recreating the assistant")
        
    except Exception as e:
        print(f"❌ Error retrieving assistant: {e}")
        print(f"  The assistant might have been deleted")
        print(f"  Run the backend to auto-create a new one")

if __name__ == "__main__":
    asyncio.run(check_assistant())

