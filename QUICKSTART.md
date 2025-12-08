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

### 3. Configure API Keys

Create `backend/.env`:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_ASSISTANT_ID=
```

### 4. Create Assistant

```bash
python create_assistant.py
```

Copy the Assistant ID to your `.env` file.

### 5. Start Backend

```bash
uvicorn main:app --reload
```

✅ Backend running at http://localhost:8000

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

