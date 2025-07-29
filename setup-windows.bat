@echo off
REM HiDock Next - Simple Windows Setup
REM Double-click this file to set up HiDock apps

echo.
echo ================================
echo   HiDock Next - Quick Setup
echo ================================
echo.
echo This will set up HiDock apps for immediate use.
echo.
pause

echo.
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
) else (
    echo Python found!
)

echo.
echo [2/4] Setting up Desktop App...
cd hidock-desktop-app
if not exist .venv (
    echo Creating Python environment...
    python -m venv .venv
)

echo Installing dependencies...
.venv\Scripts\pip install --upgrade pip setuptools wheel

echo Installing core dependencies...
.venv\Scripts\pip install pyusb customtkinter Pillow google-generativeai numpy scipy pydub matplotlib librosa

echo Installing pygame (CRITICAL for HiDock audio features)...
.venv\Scripts\pip install pygame>=2.5.0 --only-binary=:all:

if errorlevel 1 (
    echo.
    echo WARNING: pygame installation failed. Trying alternative approaches...
    
    echo Strategy 1: Force reinstall with no cache...
    .venv\Scripts\pip install pygame --force-reinstall --no-cache-dir --only-binary=:all:
    
    if errorlevel 1 (
        echo Strategy 2: Trying specific pygame version...
        .venv\Scripts\pip install pygame==2.5.2 --only-binary=:all:
        
        if errorlevel 1 (
            echo Strategy 3: Final attempt with latest pygame...
            .venv\Scripts\pip install pygame --only-binary=:all:
            
            if errorlevel 1 (
                echo.
                echo ERROR: ALL pygame installation strategies failed!
                echo pygame is MANDATORY for HiDock desktop app (audio playback).
                echo The app will NOT work without pygame.
                echo.
                echo Manual installation required:
                echo   1. .venv\Scripts\activate
                echo   2. pip install --upgrade setuptools wheel
                echo   3. pip install pygame --force-reinstall --only-binary=:all:
                echo.
                echo Or install Visual Studio Build Tools from:
                echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
                echo.
                echo Check TROUBLESHOOTING.md for more solutions.
                echo.
                pause
                exit /b 1
            )
        )
    )
)

echo Desktop app setup complete!

cd ..

echo.
echo [3/4] Checking Node.js for Web App...
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found - skipping web app setup
    echo Install Node.js 18+ from https://nodejs.org if you want the web app
) else (
    echo Node.js found! Setting up web app...
    cd hidock-web-app
    call npm install
    if errorlevel 1 (
        echo WARNING: Web app setup failed
        echo You can try running "npm install" manually in hidock-web-app folder
    ) else (
        echo Web app setup complete!
    )
    cd ..
)

echo.
echo [4/4] Setup Complete!
echo ================================
echo.
echo HOW TO RUN:
echo.
echo Desktop App:
echo   1. cd hidock-desktop-app
echo   2. .venv\Scripts\activate
echo   3. python main.py
echo.
echo Web App (if Node.js installed):
echo   1. cd hidock-web-app  
echo   2. npm run dev
echo   3. Open: http://localhost:5173
echo.
echo FIRST TIME TIPS:
echo - Configure AI providers in app Settings for transcription
echo - Connect your HiDock device via USB
echo - Check README.md and docs/TROUBLESHOOTING.md for help
echo.
echo NEED MORE? Run: python setup.py (comprehensive setup)
echo.
echo Enjoy using HiDock! 🎵
echo.
pause