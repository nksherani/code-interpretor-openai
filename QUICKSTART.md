# Quick Start Guide

Get up and running in 5 minutes! ⚡

## Prerequisites

- [x] Python 3.11+ installed
- [x] Node.js 18+ installed
- [x] OpenAI API key

## Step-by-Step

### 1. Clone & Navigate

```bash
cd openai-code-interpretor
```

### 2. Backend Setup (2 minutes)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure API Key & MongoDB

Create `backend/.env`:

```env
OPENAI_API_KEY=sk-your-key-here

# MongoDB Configuration (defaults shown)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=code-interpreter-db
MONGODB_COLLECTION_NAME=app_config
```

### 4. Start MongoDB (Quick Option)

```bash
# Using Docker (recommended)
docker run -d -p 27017:27017 mongo:latest

# Or install MongoDB locally
```

### 5. Start Backend

```bash
uvicorn main:app --reload
```

✅ Backend running at http://localhost:8000

**First run will automatically:**
- Create OpenAI Assistant
- Save to MongoDB
- Ready to use!

### 6. Frontend Setup (New Terminal)

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at http://localhost:3000

## Test It!

1. Open http://localhost:3000
2. Go to "Chat" tab
3. Type: "Calculate 10 + 20"
4. Press Send

You should get a response! 🎉

## Common Issues

**"Module not found"**
→ Make sure virtual environment is activated

**"API key not found"**
→ Check `.env` file has correct format

**"Port already in use"**
→ Close other applications using ports 8000 or 3000

## Next Steps

- Try the Examples tab
- Upload a CSV file
- Read the full README.md
- Check out API_DOCUMENTATION.md

## Need Help?

- Review SETUP_GUIDE.md for detailed instructions
- Check existing issues
- Create a new issue

---

**Time to first working app: ~5 minutes** ⏱️

