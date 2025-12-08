"""
Script to recreate the assistant with updated configuration
This will delete the old assistant ID from DB and create a new one
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
from database import connect_to_mongo, get_app_config, set_app_config, close_mongo_connection
import asyncio

load_dotenv()

async def recreate_assistant():
    """Recreate assistant with new configuration"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("🔄 Recreating assistant...")
    print()
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Get old assistant ID
    old_assistant_id = await get_app_config("assistant_id")
    if old_assistant_id:
        print(f"📌 Old assistant ID: {old_assistant_id}")
        try:
            # Try to delete old assistant (optional)
            # client.beta.assistants.delete(old_assistant_id)
            # print(f"✓ Deleted old assistant")
            pass
        except Exception as e:
            print(f"⚠ Could not delete old assistant: {e}")
    
    # Create new assistant with updated model
    print("Creating new assistant with gpt-4o-mini...")
    assistant = client.beta.assistants.create(
        name="Code Interpreter Explorer",
        instructions="""You are a helpful AI assistant with access to a Python code interpreter. 
        You can analyze data, create visualizations, perform mathematical computations, and work with files.
        Always explain your process and provide clear, detailed responses.
        When creating visualizations, save them as files so users can download them.""",
        model="gpt-4o-mini",
        tools=[{"type": "code_interpreter"}]
    )
    
    print(f"✓ Created new assistant: {assistant.id}")
    print(f"  Name: {assistant.name}")
    print(f"  Model: {assistant.model}")
    print(f"  Tools: {assistant.tools}")
    print()
    
    # Save to database
    await set_app_config("assistant_id", assistant.id)
    print(f"✓ Saved to database")
    print()
    print("✅ Assistant recreated successfully!")
    print("   Restart your backend server to use the new assistant")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(recreate_assistant())

