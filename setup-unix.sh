#!/bin/bash
# HiDock Next - Simple Linux/Mac Setup
# Run: chmod +x setup-unix.sh && ./setup-unix.sh

set -e  # Exit on any error

echo ""
echo "================================"
echo "   HiDock Next - Quick Setup"
echo "================================"
echo ""
echo "This will set up HiDock apps for immediate use."
echo ""

# Check Python
echo "[1/4] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✓ Python3 found!"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✓ Python found!"
else
    echo "❌ ERROR: Python not found!"
    echo "Please install Python 3.8+ first:"
    echo "• Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "• CentOS/RHEL: sudo dnf install python3 python3-pip"
    echo "• macOS: brew install python3 (or download from python.org)"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]; then
    echo "❌ ERROR: Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

# Set up Desktop App
echo ""
echo "[2/4] Setting up Desktop App..."
cd hidock-desktop-app

if [ ! -d ".venv" ]; then
    echo "Creating Python environment..."
    $PYTHON_CMD -m venv .venv
fi

echo "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || {
    echo ""
    echo "⚠️  WARNING: Some dependencies failed to install."
    echo "The app might still work, or you may need to install them manually."
    echo "Check TROUBLESHOOTING.md for help."
    echo ""
}

echo "✅ Desktop app setup complete!"
cd ..

# Check Node.js for Web App
echo ""
echo "[3/4] Checking Node.js for Web App..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        echo "✓ Node.js found! Setting up web app..."
        cd hidock-web-app
        npm install || {
            echo "⚠️  WARNING: Web app setup failed"
            echo "You can try running 'npm install' manually in hidock-web-app folder"
        }
        echo "✅ Web app setup complete!"
        cd ..
        WEB_APP_READY=true
    else
        echo "⚠️  Node.js version $NODE_VERSION found, but 18+ required"
        echo "Update Node.js if you want the web app"
        WEB_APP_READY=false
    fi
else
    echo "ℹ️  Node.js not found - skipping web app setup"
    echo "Install Node.js 18+ from https://nodejs.org if you want the web app"
    WEB_APP_READY=false
fi

# Complete
echo ""
echo "[4/4] Setup Complete!"
echo "================================"
echo ""
echo "🚀 HOW TO RUN:"
echo ""
echo "Desktop App:"
echo "  1. cd hidock-desktop-app"
echo "  2. source .venv/bin/activate"
echo "  3. python main.py"
echo ""

if [ "$WEB_APP_READY" = true ]; then
    echo "Web App:"
    echo "  1. cd hidock-web-app"
    echo "  2. npm run dev"
    echo "  3. Open: http://localhost:5173"
    echo ""
fi

echo "💡 FIRST TIME TIPS:"
echo "• Configure AI providers in app Settings for transcription"
echo "• Connect your HiDock device via USB"
echo "• Check README.md and docs/TROUBLESHOOTING.md for help"

# Linux USB permissions check
if [ "$(uname)" = "Linux" ]; then
    if ! groups $USER | grep -q "dialout"; then
        echo ""
        echo "⚠️  USB Permission Setup (Linux):"
        echo "For HiDock device access, run:"
        echo "  sudo usermod -a -G dialout \$USER"
        echo "Then log out and back in."
    fi
fi

echo ""
echo "🔧 NEED MORE? Run: python setup.py (comprehensive setup)"
echo ""
echo "Enjoy using HiDock! 🎵"
echo ""