"""
Script to create an OpenAI Assistant with Code Interpreter enabled.
Run this once to get your assistant ID, then add it to your .env file.
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

assistant = client.beta.assistants.create(
    name="Code Interpreter Explorer",
    instructions="""You are a helpful AI assistant with access to a Python code interpreter. 
    You can analyze data, create visualizations, perform mathematical computations, and work with files.
    Always explain your process and provide clear, detailed responses.
    When creating visualizations, save them as files so users can download them.""",
    model="gpt-4.1",
    tools=[{"type": "code_interpreter"}]
)

print(f"Assistant created successfully!")
print(f"Assistant ID: {assistant.id}")
print(f"\nAdd this to your .env file:")
print(f"OPENAI_ASSISTANT_ID={assistant.id}")


