#!/bin/bash
# HiDock Cli - Simple Linux/Mac Setup
# Run: chmod +x setup-unix.sh && ./setup-unix.sh

set -e  # Exit on any error

echo ""
echo "================================"
echo "   HiDock Cli - Quick Setup"
echo "================================"
echo ""
echo "This will set up HiDock Cli for immediate use."
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
if [ "$(printf '%s\n' "3.12" "$PYTHON_VERSION" | sort -V | tail -n1)" != "3.12" ]; then
    echo "❌ ERROR: Python 3.12 required for optimal compatibility, found $PYTHON_VERSION"
    echo "Some packages may not work with other versions"
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

echo "Upgrading pip and installing dependencies..."
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt || {
    echo ""
    echo "❌ ERROR: Failed to install dependencies!"
    echo "Check your internet connection and try again."
    echo ""
    exit 1
}

echo "✅ Desktop app setup complete!"
cd ..

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
