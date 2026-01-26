@echo off
echo ===================================================
echo   Starting TalentLens AI
echo ===================================================

echo Starting Backend Server...
start "Backend Server" cmd /k "python -m uvicorn app.main:app --reload"

echo Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Servers are starting in separate windows.
echo Backend URL: http://localhost:8000/docs
echo Frontend URL: http://localhost:5173
echo.
echo Press any key to exit this launcher (servers will keep running)...
pause >nul
