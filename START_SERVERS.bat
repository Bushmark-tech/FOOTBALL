@echo off
echo ========================================
echo Starting Football Predictor Servers
echo ========================================
echo.
echo Starting Django Server on port 8000...
echo Starting FastAPI Server on port 8001...
echo.
echo Django will be available at: http://127.0.0.1:8000
echo FastAPI will be available at: http://127.0.0.1:8001
echo FastAPI Docs at: http://127.0.0.1:8001/docs
echo.
echo Press Ctrl+C in each window to stop the servers
echo ========================================
echo.

REM Start Django server in a new window
start "Django Server" cmd /k "cd /d %~dp0 && python manage.py runserver"

REM Wait a moment for Django to start (using ping with error suppression)
ping 127.0.0.1 -n 3 >nul 2>nul

REM Start FastAPI server in a new window  
start "FastAPI Server" cmd /k "cd /d %~dp0 && python run_api.py"

echo.
echo Both servers are starting in separate windows...
echo You can close this window now.
echo.
REM Exit without pause to avoid input redirection issues in PowerShell
exit /b 0

