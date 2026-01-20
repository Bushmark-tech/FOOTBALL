# PowerShell script to start both Django and FastAPI servers
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Football Predictor Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Django Server on port 8000..." -ForegroundColor Green
Write-Host "Starting FastAPI Server on port 8001..." -ForegroundColor Green
Write-Host ""
Write-Host "Django will be available at: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "FastAPI will be available at: http://127.0.0.1:8001" -ForegroundColor Yellow
Write-Host "FastAPI Docs at: http://127.0.0.1:8001/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Start Django server in a new window
Start-Process cmd -ArgumentList "/k", "python manage.py runserver" -WindowStyle Normal

# Wait a moment for Django to start
Start-Sleep -Seconds 2

# Start FastAPI server in a new window
Start-Process cmd -ArgumentList "/k", "python run_api.py" -WindowStyle Normal

Write-Host ""
Write-Host "Both servers are starting in separate windows..." -ForegroundColor Green
Write-Host "You can close this window now." -ForegroundColor Yellow
Write-Host ""

