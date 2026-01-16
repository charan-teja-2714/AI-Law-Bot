@echo off
echo ========================================
echo Starting MediSense Frontend (React)
echo ========================================
echo.

cd frontend

echo Checking Node.js...
node --version
npm --version
echo.

echo Starting React development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm start

pause
