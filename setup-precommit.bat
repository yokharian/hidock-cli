@echo off
echo:
echo ================================
echo   Setting up Pre-commit Hooks
echo ================================
echo:

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python first.
    pause
    exit /b 1
)

REM Install pre-commit
echo Installing pre-commit...
pip install pre-commit

if %errorlevel% neq 0 (
    echo ERROR: Failed to install pre-commit!
    pause
    exit /b 1
)

REM Install the git hooks
echo:
echo Installing git hooks...
pre-commit install

if %errorlevel% neq 0 (
    echo ERROR: Failed to install git hooks!
    pause
    exit /b 1
)

echo:
echo ✅ Pre-commit hooks installed successfully!
echo:
echo The following checks will run before each commit:
echo - Flake8 (Python linting) for desktop app
echo - ESLint (JS/TS linting) for web apps
echo - Black (Python formatting)
echo - isort (Python import sorting)
echo - General file checks (trailing whitespace, large files, etc.)
echo:
echo To run hooks manually: pre-commit run --all-files
echo To skip hooks once: git commit --no-verify
echo:
pause