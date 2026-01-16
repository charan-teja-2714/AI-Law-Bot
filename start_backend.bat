@echo off
echo ========================================
echo Starting MediSense Backend (FastAPI)
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Checking Python...
python --version
echo.

cd backend

echo Starting FastAPI server on port 8000...
echo Backend will be available at: http://localhost:8000
echo API Docs will be available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
