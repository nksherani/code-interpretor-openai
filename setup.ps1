# OpenAI Code Interpreter Explorer - Windows Setup Script
# Run this script with: .\setup.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "OpenAI Code Interpreter Explorer" -ForegroundColor Cyan
Write-Host "Automated Setup Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Backend Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Setup Backend
Set-Location backend

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Yellow
    Write-Host "IMPORTANT: Environment Setup" -ForegroundColor Yellow
    Write-Host "==================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please enter your OpenAI API key:" -ForegroundColor Cyan
    $apiKey = Read-Host "API Key"
    
    Write-Host ""
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
OPENAI_API_KEY=$apiKey
OPENAI_ASSISTANT_ID=
"@ | Out-File -FilePath .env -Encoding UTF8
    
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now creating OpenAI Assistant..." -ForegroundColor Yellow
    python create_assistant.py
    
    Write-Host ""
    Write-Host "Please copy the Assistant ID from above and update your .env file" -ForegroundColor Yellow
    Write-Host "Press any key to continue once you've updated .env file..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Set-Location ..

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Frontend Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

Set-Location frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Set-Location ..

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  uvicorn main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Then open: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

