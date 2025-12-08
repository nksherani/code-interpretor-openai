# OpenAI Code Interpreter Explorer

A modern web application built with React and FastAPI to explore and interact with OpenAI's Code Interpreter capabilities. This application demonstrates data analysis, mathematical computation, visualization, and file processing using natural language.

![App Screenshot](https://via.placeholder.com/800x400?text=OpenAI+Code+Interpreter+Explorer)

## 🌟 Features

- **Interactive Chat Interface**: Chat with an AI assistant that can execute Python code
- **Data Analysis**: Upload CSV, Excel, JSON files and analyze them with natural language
- **Mathematical Computing**: Perform complex calculations, solve equations, work with sequences
- **Data Visualization**: Create charts, graphs, heatmaps, and 3D plots
- **File Operations**: Upload files, process them, and download generated outputs
- **Pre-built Examples**: Try ready-made examples showcasing different capabilities
- **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS

## 🏗️ Technology Stack

### Frontend
- React 18
- Vite (Build tool)
- Tailwind CSS (Styling)
- Axios (HTTP client)
- React Icons
- React Markdown

### Backend
- FastAPI (Python web framework)
- OpenAI API (GPT-4 with Code Interpreter)
- Uvicorn (ASGI server)
- Pydantic (Data validation)

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- OpenAI API key with access to Assistants API
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd openai-code-interpretor
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the .env.example to .env and add your keys
echo OPENAI_API_KEY=your_api_key_here > .env
echo OPENAI_ASSISTANT_ID=your_assistant_id_here >> .env
```

### 3. Start MongoDB (Optional - defaults to localhost)

The application will automatically use MongoDB for storing the assistant configuration.

**Option 1: Local MongoDB**
```bash
# Install MongoDB locally or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Option 2: MongoDB Atlas (Cloud)**
Add to your `.env`:
```
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE_NAME=code-interpreter-db
MONGODB_COLLECTION_NAME=app_config
```

**Option 3: Use default localhost**
Just start the backend - it will try to connect to `mongodb://localhost:27017`

### 4. Start Backend Server

```bash
# Make sure you're in the backend directory with venv activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Note:** On first run, the application will automatically:
- Connect to MongoDB
- Check if an assistant exists in the database
- Create a new assistant if needed
- Save the assistant ID to MongoDB for future use

No manual assistant creation required! 🎉

### 5. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

## 🔄 MongoDB Integration

The application now uses MongoDB to automatically manage assistant configuration:
- ✅ **No manual assistant creation required**
- ✅ **Assistant auto-created on first run**
- ✅ **Persistent storage in database**
- ✅ **Easy to scale for multi-tenant use**

See [MONGODB_INTEGRATION.md](MONGODB_INTEGRATION.md) for detailed setup options.

## 📖 Usage Guide

### Chat Interface

1. Navigate to the "Chat" tab
2. Type your question or request (e.g., "Calculate the first 20 Fibonacci numbers")
3. The AI will execute Python code and return results
4. Download any generated files (charts, data files, etc.)

**Example prompts:**
- "Create a bar chart showing sales data for 5 products"
- "Solve the equation: x^3 - 6x^2 + 11x - 6 = 0"
- "Generate a scatter plot with correlation coefficient"

### Examples

1. Navigate to the "Examples" tab
2. Choose from pre-built examples:
   - **Data Analysis**: Generate and analyze sample sales data
   - **Mathematical Computing**: Fibonacci, primes, equation solving
   - **Data Visualization**: Heatmaps, 3D plots, pie charts
3. Click "Run Example" and view results
4. Download generated visualizations

### File Upload

1. Navigate to the "File Upload" tab
2. Drag and drop files or click to upload
3. Supported formats: CSV, Excel (.xlsx, .xls), JSON, TXT, PDF
4. Enter your analysis request (e.g., "Show me summary statistics and trends")
5. Click "Analyze Data"
6. View results and download any generated files

## 🔧 API Endpoints

### Chat
- `POST /api/chat` - Send a message and get AI response
- `POST /api/thread/create` - Create a new conversation thread
- `GET /api/thread/{thread_id}/messages` - Get thread history

### File Operations
- `POST /api/upload` - Upload a file
- `GET /api/file/{file_id}` - Download a generated file

### Analysis
- `POST /api/analyze` - Analyze data with optional file attachments

### Examples
- `POST /api/examples/data-analysis` - Run data analysis example
- `POST /api/examples/math-computation` - Run math example
- `POST /api/examples/image-generation` - Run visualization example

## 🎨 Customization

### Modify Assistant Instructions

Edit `backend/create_assistant.py` to change the assistant's behavior:

```python
assistant = client.beta.assistants.create(
    name="Code Interpreter Explorer",
    instructions="Your custom instructions here...",
    model="gpt-4-turbo-preview",
    tools=[{"type": "code_interpreter"}]
)
```

### Add New Examples

Add new examples in `backend/main.py`:

```python
@app.post("/api/examples/custom-example")
async def example_custom():
    prompt = "Your custom prompt here..."
    request = AnalysisRequest(prompt=prompt)
    return await analyze_data(request)
```

### Styling

The frontend uses Tailwind CSS. Modify `frontend/tailwind.config.js` to customize colors and themes.

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with auto-reload
uvicorn main:app --reload

# Run tests (if you add them)
pytest
```

### Frontend Development

```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📦 Production Deployment

### Backend (FastAPI)

```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Run with gunicorn (production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (React)

```bash
cd frontend

# Build for production
npm run build

# The dist/ folder contains optimized static files
# Deploy to Netlify, Vercel, or any static hosting
```

### Environment Variables for Production

Set these environment variables in your production environment:

- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_ASSISTANT_ID` - Your Assistant ID

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for the powerful Code Interpreter API
- FastAPI for the excellent Python web framework
- React team for the amazing frontend library
- Tailwind CSS for the utility-first CSS framework

## 📞 Support

If you have questions or need help:

1. Check the documentation
2. Search existing issues
3. Create a new issue with details about your problem

## 🔒 Security

- Never commit your `.env` file or API keys
- Use environment variables for sensitive data
- Keep your OpenAI API key secure
- Review the code before running examples with your data

## ⚠️ Rate Limits

Be aware of OpenAI API rate limits:
- Assistants API has specific rate limits
- Code Interpreter operations can take time
- Monitor your usage in the OpenAI dashboard

## 🎯 Roadmap

- [ ] Add user authentication
- [ ] Support for more file formats
- [ ] Conversation history persistence
- [ ] Export chat transcripts
- [ ] Custom assistant configurations
- [ ] Multi-language support
- [ ] Advanced data visualization options
- [ ] Collaborative features

## 💡 Tips

1. **Be Specific**: The more specific your prompts, the better the results
2. **Iterate**: Start simple, then add complexity based on initial results
3. **Save Results**: Download important files immediately
4. **Use Examples**: Start with examples to understand capabilities
5. **Error Handling**: If something fails, try rephrasing your request

---

**Built with ❤️ using React, FastAPI, and OpenAI**

