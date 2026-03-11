@echo off
title TEW Booking ^& Finance Optimizer v4.0
cd /d "%~dp0"

echo ========================================
echo   TEW Booking ^& Finance Optimizer v4.0
echo ========================================
echo.

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+ first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install/update dependencies
echo Installing dependencies (first start may take a minute)...
py -m pip install -r requirements.txt --no-input --disable-pip-version-check
echo.

echo Starting TEW Optimizer...
echo The app will open in your browser at: http://localhost:8501
echo Close this window or press Ctrl+C to stop.
echo.

start "" http://localhost:8501
py -m streamlit run app.py --server.port 8501 --server.headless true

pause
