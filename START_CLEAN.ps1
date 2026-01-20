# Start both Django and FastAPI servers
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Football Predictor - Both Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing Python processes on ports 8000 and 8001
Write-Host "Cleaning up existing servers..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "Stopped process on port 8000" -ForegroundColor Green
}

$port8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($port8001) {
    Stop-Process -Id $port8001.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "Stopped process on port 8001" -ForegroundColor Green
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Django Server (Port 8000)..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Start Django server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python manage.py runserver" -WindowStyle Normal

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting FastAPI Server (Port 8001)..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Start FastAPI server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python run_api.py" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Both servers are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Django:  http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "FastAPI: http://127.0.0.1:8001" -ForegroundColor Yellow
Write-Host ""
Write-Host "Close the PowerShell windows to stop the servers." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
