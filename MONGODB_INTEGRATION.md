# MongoDB Integration Guide

The application now uses MongoDB to automatically manage the OpenAI Assistant configuration. No more manual assistant creation! 🎉

## What Changed?

### Before (Manual Process)
1. Run `create_assistant.py`
2. Copy Assistant ID
3. Paste into `.env` file
4. Start application

### After (Automatic)
1. Start MongoDB
2. Start application
3. ✨ Done! Assistant is auto-created and saved

## How It Works

### On Application Startup:

```
1. Connect to MongoDB
2. Check database for existing assistant_id
3. If found → Verify it exists in OpenAI → Use it
4. If not found → Create new assistant → Save to MongoDB
5. Ready to use!
```

### Database Schema

```javascript
// Database: code-interpreter-db (configurable)
// Collection: app_config (configurable)
{
  "_id": ObjectId("..."),
  "key": "assistant_id",
  "value": "asst_abc123xyz..."
}
```

You can customize the database and collection names via environment variables.

## Setup Options

### Option 1: Local MongoDB (Docker - Easiest)

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

Then start your backend:
```bash
cd backend
uvicorn main:app --reload
```

### Option 2: Local MongoDB (Installed)

1. Download from [MongoDB Community](https://www.mongodb.com/try/download/community)
2. Install and start MongoDB service
3. Application connects to `mongodb://localhost:27017` by default

### Option 3: MongoDB Atlas (Cloud - Free Tier)

1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get connection string
4. Add to `backend/.env`:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
```

### Option 4: Docker Compose (All-in-One)

Start everything at once:
```bash
docker-compose up
```

This starts:
- MongoDB on port 27017
- Backend on port 8000
- Frontend on port 3000

## Configuration

### Environment Variables

**backend/.env:**
```env
# Required
OPENAI_API_KEY=sk-your-api-key-here

# MongoDB Configuration (with defaults)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=code-interpreter-db
MONGODB_COLLECTION_NAME=app_config
```

### Custom MongoDB Configuration

**Local MongoDB with authentication:**
```env
MONGODB_CONNECTION_STRING=mongodb://username:password@localhost:27017/
MONGODB_DATABASE_NAME=code-interpreter-db
MONGODB_COLLECTION_NAME=app_config
```

**MongoDB Atlas (Cloud):**
```env
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE_NAME=code-interpreter-db
MONGODB_COLLECTION_NAME=app_config
```

**Custom host/port:**
```env
MONGODB_CONNECTION_STRING=mongodb://192.168.1.100:27017/
MONGODB_DATABASE_NAME=my-custom-db
MONGODB_COLLECTION_NAME=my-config
```

### Configuration Flexibility

Each component can be customized independently:
- **Connection String**: Where MongoDB is hosted
- **Database Name**: Which database to use
- **Collection Name**: Which collection stores app config

## New Files Added

### `backend/database.py`
- MongoDB connection management
- Database utilities
- App config get/set functions

### `backend/assistant_manager.py`
- Assistant lifecycle management
- Auto-creation logic
- OpenAI client wrapper

### Modified Files

### `backend/main.py`
- Added lifespan manager for startup/shutdown
- Removed hardcoded assistant ID
- Uses dynamic assistant from MongoDB

## Benefits

✅ **No Manual Steps** - Assistant created automatically
✅ **Persistent** - Assistant ID saved in database
✅ **Resilient** - Verifies assistant exists before using
✅ **Scalable** - Easy to extend for multi-tenant use
✅ **Professional** - Production-ready configuration management

## Startup Log Example

```
🚀 Starting application...
✓ Connected to MongoDB at mongodb://localhost:27017
✓ Created new assistant: asst_abc123xyz...
✓ Application ready with assistant: asst_abc123xyz...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Or if assistant already exists:
```
🚀 Starting application...
✓ Connected to MongoDB at mongodb://localhost:27017
✓ Using existing assistant: asst_abc123xyz...
✓ Application ready with assistant: asst_abc123xyz...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Viewing Your Data

### Using MongoDB Compass (GUI)

1. Download [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Connect to `mongodb://localhost:27017`
3. Browse `code_interpreter_db` → `app_config`

### Using MongoDB Shell

```bash
# Connect
mongosh

# Switch to database (use your configured database name)
use code-interpreter-db

# View config (use your configured collection name)
db.app_config.find().pretty()

# Output:
{
  _id: ObjectId("..."),
  key: 'assistant_id',
  value: 'asst_abc123xyz...'
}
```

**Note:** Database and collection names are configurable via environment variables.

## Troubleshooting

### "Connection refused to MongoDB"

**Problem:** MongoDB not running

**Solution:**
```bash
# Start MongoDB with Docker
docker run -d -p 27017:27017 mongo:latest

# Or check local MongoDB service
# Windows: services.msc → MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

### "No assistant_id in database but one exists in OpenAI"

**Problem:** Database empty but you have existing assistant

**Solution:** The app will create a new one. To use existing:
```bash
mongosh
use code_interpreter_db
db.app_config.insertOne({
  key: "assistant_id",
  value: "asst_your_existing_id"
})
```

### "Assistant verification failed"

**Problem:** Assistant ID in DB doesn't exist in OpenAI

**Solution:** The app automatically creates a new one. Old ID is overwritten.

## Migration from Old Setup

If you were using the manual assistant creation:

### Your old `.env`:
```env
OPENAI_API_KEY=sk-...
OPENAI_ASSISTANT_ID=asst_abc123
```

### New `.env`:
```env
OPENAI_API_KEY=sk-...
# OPENAI_ASSISTANT_ID no longer needed!
```

### To preserve your existing assistant:

```bash
# Connect to MongoDB
mongosh

# Save your existing assistant ID
use code_interpreter_db
db.app_config.insertOne({
  key: "assistant_id",
  value: "asst_abc123"
})
```

## Future Enhancements

This MongoDB integration makes it easy to add:

### Per-User Assistants
```python
async def get_user_assistant(user_id: str):
    config = await db.user_assistants.find_one({"user_id": user_id})
    if not config:
        assistant_id = await create_assistant_for_user(user_id)
        await db.user_assistants.insert_one({
            "user_id": user_id,
            "assistant_id": assistant_id
        })
```

### Multiple Assistant Types
```python
assistant_types = {
    "data_analyst": "Specialized in data analysis",
    "math_expert": "Specialized in mathematics",
    "visualizer": "Specialized in visualizations"
}
```

### Usage Tracking
```python
await db.usage_stats.insert_one({
    "assistant_id": assistant_id,
    "user_id": user_id,
    "request_type": "chat",
    "timestamp": datetime.now()
})
```

## Testing

### Test MongoDB Connection

```bash
cd backend
python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('mongodb://localhost:27017').admin.command('ping')); print('✓ MongoDB connected!')"
```

### Test Assistant Creation

```bash
# Start backend and check logs
uvicorn main:app --reload

# Should see:
# ✓ Created new assistant: asst_...
```

## Security Notes

- MongoDB connection string may contain credentials
- Keep `MONGODB_URL` in `.env` file (not committed to git)
- Use environment variables in production
- Consider MongoDB authentication for production deployments

## Resources

- [MongoDB Docs](https://docs.mongodb.com/)
- [Motor (Async Driver) Docs](https://motor.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview)

---

**Questions?** Check the main README.md or create an issue!

