#!/bin/bash
# HiDock Next - Cleanup Script for Testing
# Removes all build artifacts and dependencies for fresh testing

echo ""
echo "================================"
echo "   HiDock Next - Cleanup Script"
echo "================================"
echo ""
echo "This will remove all build artifacts and dependencies."
echo "Use this before testing setup scripts."
echo ""
read -p "Press Enter to continue..."

echo ""
echo "Cleaning up Desktop App..."
cd hidock-desktop-app

if [ -d ".venv" ]; then
    echo "Removing Python virtual environment..."
    rm -rf .venv
    echo "✓ .venv removed"
else
    echo "ℹ️  No .venv found"
fi

if [ -d "__pycache__" ]; then
    echo "Removing Python cache..."
    rm -rf __pycache__
    echo "✓ __pycache__ removed"
fi

# Remove all __pycache__ directories recursively
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove .pyc files
find . -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "✅ Cleanup Complete!"
echo ""
echo "All build artifacts and dependencies removed."
echo "Ready for fresh setup testing."
echo ""
