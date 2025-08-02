@echo off
REM HiDock Next - Cleanup Script for Testing
REM Removes all build artifacts and dependencies for fresh testing

echo.
echo ================================
echo   HiDock Next - Cleanup Script
echo ================================
echo.
echo This will remove all build artifacts and dependencies.
echo Use this before testing setup scripts.
echo.
pause

echo.
echo Cleaning up Desktop App...
cd hidock-desktop-app
if exist .venv (
    echo Removing Python virtual environment...
    rmdir /s /q .venv
    echo Python venv removed
) else (
    echo No .venv found
)

if exist __pycache__ (
    echo Removing Python cache...
    rmdir /s /q __pycache__
    echo Python cache removed
)

for /d %%i in (*__pycache__*) do (
    if exist "%%i" (
        echo Removing %%i...
        rmdir /s /q "%%i"
    )
)

if exist *.pyc (
    echo Removing .pyc files...
    del /q *.pyc
)

echo.
echo Cleanup Complete!
echo.
echo All build artifacts and dependencies removed.
echo Ready for fresh setup testing.
echo.
pause
