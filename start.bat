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

REM Check Python version (recommend 3.10-3.13)
echo Checking Python version...
py -c "import sys; v=sys.version_info; exit(0 if 10<=v.minor<=13 else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python 3.10-3.13 recommended. Newer versions may have issues installing pyodbc.
    echo Download Python 3.12: https://www.python.org/downloads/release/python-3129/
    echo.
)

REM Install/update dependencies
echo Installing dependencies (first start may take a minute)...
py -m pip install -r requirements.txt --no-input --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo [ERROR] Some dependencies failed to install.
    echo.
    echo Common fix for pyodbc errors:
    echo   1. Use Python 3.12 (recommended): https://www.python.org/downloads/release/python-3129/
    echo   2. Or install Microsoft C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo   3. Then re-run this script.
    echo.
    pause
    exit /b 1
)
echo.

echo Starting TEW Optimizer...
echo The app will open in your browser at: http://localhost:8501
echo Close this window or press Ctrl+C to stop.
echo.

start "" http://localhost:8501
py -m streamlit run app.py --server.port 8501 --server.headless true

pause
