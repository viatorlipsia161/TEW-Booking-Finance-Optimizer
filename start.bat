@echo off
title TEW Booking ^& Finance Optimizer v4.0
cd /d "%~dp0"

echo ============================================
echo   TEW Booking ^& Finance Optimizer v4.0
echo ============================================
echo.

REM ── Step 1: Check if Python is installed ──
echo [1/4] Checking Python...
py --version >nul 2>&1
if errorlevel 1 goto :err_no_python
for /f "tokens=*" %%i in ('py --version 2^>^&1') do echo       Found: %%i

REM ── Step 2: Check Python version ──
echo [2/4] Checking Python version...
py -c "import sys; v=sys.version_info; exit(0 if v.major==3 and v.minor>=10 else 1)" >nul 2>&1
if errorlevel 1 goto :warn_python_version

:step3
REM ── Step 3: Install dependencies ──
echo [3/4] Installing dependencies (first start may take a few minutes)...
echo.
py -m pip install --upgrade pip >nul 2>&1
py -m pip install -r requirements.txt --no-input --disable-pip-version-check
if errorlevel 1 goto :err_deps
echo.

REM ── Step 3b: Verify critical modules ──
echo       Verifying modules...
py -c "import streamlit" >nul 2>&1
if errorlevel 1 goto :err_streamlit
py -c "import pyodbc" >nul 2>&1
if errorlevel 1 goto :err_pyodbc
echo       All modules OK!
echo.

REM ── Step 4: Launch the app ──
echo [4/4] Starting TEW Optimizer...
echo.
echo ============================================
echo   The app will open in your browser at:
echo   http://localhost:8501
echo.
echo   Close this window or press Ctrl+C to stop.
echo ============================================
echo.
py -m streamlit run app.py --server.port 8501
goto :end

REM ════════════════════════════════════════════
REM  Error handlers (outside of if-blocks to
REM  avoid CMD parser issues with special chars)
REM ════════════════════════════════════════════

:err_no_python
echo.
echo [ERROR] Python is not installed or not in PATH!
echo.
echo How to fix:
echo   1. Download Python 3.12 from:
echo      https://www.python.org/downloads/release/python-3129/
echo   2. Run the installer
echo   3. IMPORTANT: Check "Add Python to PATH" at the bottom!
echo   4. Restart your PC, then run this script again.
echo.
pause
exit /b 1

:warn_python_version
echo.
echo [WARNING] Your Python version may be too old. Python 3.10+ is required.
echo.
echo If you have issues, download Python 3.12 from:
echo   https://www.python.org/downloads/release/python-3129/
echo.
echo Press any key to continue anyway, or close this window to cancel...
pause >nul
echo.
goto :step3

:err_deps
echo.
echo [ERROR] Some dependencies failed to install!
echo.
echo Common fixes:
echo   1. Use Python 3.12: https://www.python.org/downloads/release/python-3129/
echo   2. If pyodbc fails, install Microsoft C++ Build Tools:
echo      https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo   3. Then re-run this script.
echo.
pause
exit /b 1

:err_streamlit
echo.
echo [ERROR] streamlit module not found even after install!
echo.
echo This usually means pip installed to a different Python version.
echo.
echo How to fix:
echo   1. Make sure you only have ONE Python version installed
echo   2. Or run manually:  py -3.12 -m pip install -r requirements.txt
echo   3. Then:             py -3.12 -m streamlit run app.py
echo.
pause
exit /b 1

:err_pyodbc
echo.
echo [ERROR] pyodbc module not found!
echo.
echo How to fix:
echo   1. Use Python 3.12: https://www.python.org/downloads/release/python-3129/
echo   2. Or install Microsoft C++ Build Tools:
echo      https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo   3. Then re-run this script.
echo.
pause
exit /b 1

:end
pause