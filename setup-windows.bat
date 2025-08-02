@echo off
REM HiDock Next - Simple Windows Setup
REM Double-click this file to set up HiDock apps

echo:
echo ================================
echo   HiDock Next - Quick Setup
echo ================================
echo:
echo This will set up HiDock apps for immediate use.
echo:
pause

echo:
echo [1/3] Checking Python...
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.12 not found!
    echo HiDock requires Python 3.12 for optimal compatibility.
    echo Please install Python 3.12 from https://python.org
    echo Available versions: py -0
    pause
    exit /b 1
) else (
    echo Python 3.12 found!
)

echo:
echo [2/3] Setting up Desktop App...
cd hidock-desktop-app
if not exist .venv (
    echo Creating Python environment...
    py -3.12 -m venv .venv
)

echo Upgrading pip and installing build tools...
.venv\Scripts\python -m pip install --upgrade pip setuptools wheel

echo Installing dependencies (this may take a few minutes)...
.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo:
    echo ERROR: Failed to install dependencies!
    echo Check your internet connection and try again.
    echo:
    pause
    exit /b 1
)

echo Desktop app setup complete!

cd ..

echo:
echo [3/3] Setup Complete!
echo ================================
echo:
echo HOW TO RUN:
echo:
echo Desktop App:
echo   1. cd hidock-desktop-app
echo   2. .venv\Scripts\activate
echo   3. python main.py
echo:
echo FIRST TIME TIPS:
echo - Configure AI providers in app Settings for transcription
echo - Connect your HiDock device via USB
echo - Check README.md and docs/TROUBLESHOOTING.md for help
echo:
echo NEED MORE? Run: python setup.py (comprehensive setup)
echo:
echo Enjoy using HiDock! 🎵
echo:
pause
