# 🚀 Quick Start Guide

**Get HiDock Next running in under 5 minutes!**

Choose the setup method that works best for you:

## 🚀 Super Simple Setup (End Users)

**Just want to use HiDock apps? Pick your platform:**

### 🪟 Windows (Double-click)
```cmd
setup-windows.bat
```
Double-click the `setup-windows.bat` file in Windows Explorer.

### 🐧🍎 Linux/Mac (Terminal)
```bash
chmod +x setup-unix.sh && ./setup-unix.sh
```

### 🐍 Any Platform (Python)
```bash
python setup.py
# Choose option 1 (End User)
```

**Requirements:** Python 3.12+ recommended (minimum 3.8)

## 👨‍💻 Developer Setup

**Want to contribute code?**

```bash
python setup.py
# Choose option 2 (Developer)
```

This includes:
- Full development environment with virtual environments
- Pre-commit hooks for automated code quality
- Git workflow setup with proper branching
- Testing tools (pytest, vitest) with coverage
- AI API key configuration and validation
- Code formatting tools (Black, ESLint) with 120-char line length

## 📱 What You Get

After setup, you can run:

### Desktop Application
```bash
cd hidock-desktop-app
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

python main.py
```

### Web Application
```bash
cd hidock-web-app
npm run dev
# Open: http://localhost:5173
```

## ❓ Need Help?

- **Problems during setup?** → [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **How to use the apps?** → [README.md](README.md)
- **Want to contribute?** → [CONTRIBUTING.md](CONTRIBUTING.md)
- **Pre-commit issues?** → [docs/PRE-COMMIT.md](docs/PRE-COMMIT.md)

## 🎯 Quick Tips

- **Desktop app**: Best for full features and local AI models
- **Web app**: Great for quick access and device management
- **AI providers**: Configure in app Settings for transcription
- **HiDock device**: Connect via USB for device management
- **Code quality**: Pre-commit hooks run automatically on commit
- **Line length**: 120 characters standard across all code

## 🔧 Developer Quick Commands

After developer setup:

```bash
# Test everything
cd hidock-desktop-app && python -m pytest tests/ -v
cd hidock-web-app && npm test

# Check code quality
pre-commit run --all-files

# Format code
cd hidock-desktop-app && black . && isort .
cd hidock-web-app && npm run lint
```
