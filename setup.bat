@echo off
echo Starting Nymble Setup (Windows)...

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

IF EXIST backend\requirements.txt (
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt
) ELSE (
    echo requirements.txt not found. Skipping dependency installation.
)

echo Setup complete! To run the backend server:
echo call venv\Scripts\activate
echo cd backend ^&^& uvicorn main:app --reload
pause
