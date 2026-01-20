@echo off
echo ========================================
echo Starting Football Predictor Locally
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Checking Python...
python --version
echo.

echo Step 2: Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated!
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment created and activated!
)
echo.

echo Step 3: Installing/updating dependencies...
pip install -r requirements.txt
echo.

echo Step 4: Running migrations...
python manage.py migrate
echo.

echo Step 5: Starting development server...
echo.
echo ========================================
echo Server starting at http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver

pause

