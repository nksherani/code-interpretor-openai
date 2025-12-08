# Complete Setup Guide

This guide will walk you through setting up the OpenAI Code Interpreter Explorer from scratch.

## Prerequisites Check

Before starting, make sure you have:

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] OpenAI API account with API key
- [ ] Code editor (VS Code recommended)

## Step 1: Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (you won't be able to see it again!)
6. Save it securely

## Step 2: Project Setup

### Clone or Download

```bash
# If using Git
git clone <repository-url>
cd openai-code-interpretor

# Or download and extract the ZIP file
```

### Project Structure

Your project should look like this:

```
openai-code-interpretor/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── create_assistant.py
│   └── .env (you'll create this)
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Step 3: Backend Setup

### 3.1 Navigate to Backend

```bash
cd backend
```

### 3.2 Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (server)
- OpenAI SDK
- Other dependencies

### 3.4 Create Environment File

Create a file named `.env` in the backend directory:

**Windows:**
```powershell
New-Item -Path .env -ItemType File
```

**macOS/Linux:**
```bash
touch .env
```

Edit `.env` and add:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_ASSISTANT_ID=
```

### 3.5 Create OpenAI Assistant

Run the assistant creation script:

```bash
python create_assistant.py
```

You should see output like:

```
Assistant created successfully!
Assistant ID: asst_abc123xyz...

Add this to your .env file:
OPENAI_ASSISTANT_ID=asst_abc123xyz...
```

Copy the Assistant ID and update your `.env` file:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_ASSISTANT_ID=asst_abc123xyz...
```

### 3.6 Test Backend Server

Start the server:

```bash
uvicorn main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Test it by visiting: http://localhost:8000

You should see:
```json
{"message": "OpenAI Code Interpreter Explorer API"}
```

**Keep this terminal open and running!**

## Step 4: Frontend Setup

### 4.1 Open New Terminal

Open a new terminal window/tab (keep backend running in the other one)

### 4.2 Navigate to Frontend

```bash
cd frontend
```

(Adjust path based on where you are. If you were in backend, do `cd ../frontend`)

### 4.3 Install Node Dependencies

```bash
npm install
```

This will install:
- React and React DOM
- Vite
- Tailwind CSS
- Axios
- Other frontend dependencies

This may take a few minutes.

### 4.4 Start Development Server

```bash
npm run dev
```

You should see:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

## Step 5: Open the Application

1. Open your browser
2. Go to: http://localhost:3000
3. You should see the OpenAI Code Interpreter Explorer interface!

## Step 6: Test the Application

### Test 1: Chat Interface

1. Click on "Chat" tab
2. Try a simple prompt: "Calculate 5 + 5"
3. You should get a response from the AI

### Test 2: Run an Example

1. Click on "Examples" tab
2. Click "Run Example" on any example
3. Wait for results (this may take 10-30 seconds)
4. You should see analysis results

### Test 3: File Upload

1. Click on "File Upload" tab
2. Create a simple test CSV file:

```csv
name,value
A,10
B,20
C,15
```

3. Upload it
4. Ask: "Show me a bar chart of this data"
5. You should get a visualization

## Troubleshooting

### Backend Issues

**Problem: `ModuleNotFoundError: No module named 'fastapi'`**

Solution:
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt
pip install -r requirements.txt
```

**Problem: `OpenAI API key not found`**

Solution:
- Check that `.env` file exists in backend directory
- Check that `OPENAI_API_KEY` is set correctly
- No spaces around the `=` sign
- API key starts with `sk-`

**Problem: `Port 8000 already in use`**

Solution:
```bash
# Use a different port
uvicorn main:app --reload --port 8001

# Update frontend proxy in vite.config.js to match
```

### Frontend Issues

**Problem: `Cannot GET /`**

Solution:
- Make sure you're accessing http://localhost:3000 (not 8000)
- Check that `npm run dev` is running
- Try `npm install` again

**Problem: API errors in browser console**

Solution:
- Make sure backend is running on port 8000
- Check browser console for specific error
- Verify `.env` file has both API key and Assistant ID

**Problem: `npm install` fails**

Solution:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### OpenAI API Issues

**Problem: Rate limit errors**

Solution:
- Wait a few seconds between requests
- Check your OpenAI usage dashboard
- Upgrade your OpenAI plan if needed

**Problem: Assistant not responding**

Solution:
- Check OpenAI API status page
- Verify your API key is valid
- Check that you have available credits

## Development Workflow

### Daily Development

1. **Start Backend** (Terminal 1):
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```

2. **Start Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

### Stopping the Application

1. Press `Ctrl+C` in both terminals
2. Deactivate Python virtual environment:
```bash
deactivate
```

## Next Steps

Now that everything is working:

1. ✅ Explore the Chat Interface
2. ✅ Try all the Examples
3. ✅ Upload and analyze your own files
4. ✅ Read the About section in the app
5. ✅ Check out the API documentation at http://localhost:8000/docs

## Getting Help

If you're still having issues:

1. Check the error messages carefully
2. Review this guide step by step
3. Check the main README.md for additional info
4. Ensure all prerequisites are met
5. Try restarting both servers

## Security Reminders

- ⚠️ Never commit your `.env` file
- ⚠️ Keep your API key secret
- ⚠️ Don't share your Assistant ID publicly
- ⚠️ Monitor your OpenAI usage

## Success Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Can access http://localhost:3000 in browser
- [ ] Chat interface responds to messages
- [ ] Examples run successfully
- [ ] File upload works
- [ ] No console errors

Congratulations! You've successfully set up the OpenAI Code Interpreter Explorer! 🎉

