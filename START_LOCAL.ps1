# Football Predictor - Local Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Football Predictor Locally" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to script directory
Set-Location $PSScriptRoot

# Check Python
Write-Host "Step 1: Checking Python..." -ForegroundColor Yellow
python --version
Write-Host ""

# Activate virtual environment
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment created and activated!" -ForegroundColor Green
}
Write-Host ""

# Install dependencies
Write-Host "Step 3: Installing/updating dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host ""

# Run migrations
Write-Host "Step 4: Running migrations..." -ForegroundColor Yellow
python manage.py migrate
Write-Host ""

# Start server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server starting at http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver

