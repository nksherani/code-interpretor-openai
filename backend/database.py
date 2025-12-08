"""
Database configuration and utilities for MongoDB
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None
    collection_name = None

db_instance = Database()

async def connect_to_mongo():
    """Connect to MongoDB"""
    # Get configuration from environment variables
    mongodb_url = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DATABASE_NAME", "code-interpreter-db")
    collection_name = os.getenv("MONGODB_COLLECTION_NAME", "app_config")
    
    # Connect to MongoDB
    db_instance.client = AsyncIOMotorClient(mongodb_url)
    db_instance.db = db_instance.client[db_name]
    db_instance.collection_name = collection_name
    
    print(f"✓ Connected to MongoDB at {mongodb_url}")
    print(f"✓ Using database: {db_name}")
    print(f"✓ Using collection: {collection_name}")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db_instance.client:
        db_instance.client.close()
        print("✓ Closed MongoDB connection")

def get_database():
    """Get database instance"""
    return db_instance.db

def get_collection():
    """Get the configured collection"""
    return db_instance.db[db_instance.collection_name]

async def get_app_config(key: str):
    """Get app configuration value from database"""
    collection = get_collection()
    config = await collection.find_one({"key": key})
    return config["value"] if config else None

async def set_app_config(key: str, value: str):
    """Set app configuration value in database"""
    collection = get_collection()
    await collection.update_one(
        {"key": key},
        {"$set": {"key": key, "value": value}},
        upsert=True
    )

