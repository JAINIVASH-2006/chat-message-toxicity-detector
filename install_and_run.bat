@echo off
echo.
echo ================================================================
echo 🔥 Enhanced Toxicity Analysis System - Windows Installer
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo 🐍 Python found, proceeding with installation...
echo.

REM Install dependencies
echo 📦 Installing dependencies...
python install_requirements.py
if %errorlevel% neq 0 (
    echo ⚠️ Warning: Some dependencies may not have installed correctly
    echo Continuing anyway...
)

echo.
echo 🚀 Starting Enhanced Toxicity Analysis System...
echo 🌐 Your browser should open automatically
echo 📱 Manual access: http://localhost:5000
echo.

REM Start the application
python app_stable.py

echo.
echo 👋 Application stopped
pause
