@echo off
REM GuardianAI - Quick Start Script for Windows

echo.
echo ===============================================
echo  🛡️  GuardianAI - Social Media Scam Detector
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if venv exists, if not create it
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment found
)

echo.

REM Activate venv
echo 🚀 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📌 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo ===============================================
echo  🎉 Setup Complete!
echo ===============================================
echo.
echo Starting GuardianAI server...
echo.
echo 🌐 Open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask app
python server.py
