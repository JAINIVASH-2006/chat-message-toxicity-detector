@echo off
REM ========================================
REM  Quick Start with Chrome Launch
REM ========================================

echo Starting Enhanced Toxicity Analysis System...
cd /d "%~dp0"

REM Check setup
if not exist ".venv\Scripts\activate.bat" (
    echo Running setup first...
    call SETUP.bat
    if errorlevel 1 exit /b 1
)

REM Activate and check port
call .venv\Scripts\activate.bat

netstat -ano | findstr :5000 | findstr LISTENING >nul
if not errorlevel 1 (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM Start server in background
echo Starting server...
start /b python app.py

REM Wait for server to be ready
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

REM Check if server is running
python -c "import requests; requests.get('http://127.0.0.1:5000', timeout=5)" >nul 2>&1
if errorlevel 1 (
    echo Waiting a bit longer...
    timeout /t 3 /nobreak >nul
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    Server Started!                         ║
echo ║            Opening in Chrome browser...                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Open Chrome
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://127.0.0.1:5000"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" "http://127.0.0.1:5000"
) else (
    start http://127.0.0.1:5000
)

echo.
echo Application is running at: http://127.0.0.1:5000
echo.
echo Press any key to stop the server...
pause >nul

REM Kill the server
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo Server stopped.
