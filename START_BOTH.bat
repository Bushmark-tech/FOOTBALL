@echo off
echo ========================================
echo Starting Football Predictor - Both Services
echo ========================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo Starting Django Server (Port 8000)...
echo ========================================
start "Django Server" cmd /k "python manage.py runserver"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting FastAPI Server (Port 8001)...
echo ========================================
start "FastAPI Server" cmd /k "python run_api.py"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Django: http://127.0.0.1:8000
echo FastAPI: http://127.0.0.1:8001
echo.
echo Close the windows to stop the servers.
echo ========================================
pause

