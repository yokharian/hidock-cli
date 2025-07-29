# Quick Start Guide

Choose the setup method that works best for you:

## 🚀 Super Simple Setup (End Users)

**Just want to use HiDock apps? Pick your platform:**

### Windows (Double-click)
```cmd
setup-windows.bat
```
Double-click the `setup-windows.bat` file in Windows Explorer.

### Linux/Mac (Terminal)
```bash
chmod +x setup-unix.sh && ./setup-unix.sh
```

### Any Platform (Python)
```bash
python setup.py
# Choose option 1 (End User)
```

## 👨‍💻 Developer Setup

**Want to contribute code?**

```bash
python setup.py
# Choose option 2 (Developer)
```

This includes:
- Full development environment
- Git workflow setup
- Testing tools
- AI API key configuration
- Code formatting tools

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

- **Problems during setup?** → [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **How to use the apps?** → [README.md](README.md)
- **Want to contribute?** → [CONTRIBUTING.md](CONTRIBUTING.md)

## 🎯 Quick Tips

- **Desktop app**: Best for full features and local AI models
- **Web app**: Great for quick access and device management
- **AI providers**: Configure in app Settings for transcription
- **HiDock device**: Connect via USB for device management