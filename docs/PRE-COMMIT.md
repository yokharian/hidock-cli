# Pre-commit Hooks Setup

This project uses pre-commit hooks to ensure code quality before commits.

## Quick Setup

### Windows
```bash
.\setup-precommit.bat
```

### Linux/Mac
```bash
./setup-precommit.sh
```

## What Gets Checked

Before each commit, the following checks run automatically:

### Python Code (Desktop App)
- **Flake8**: Code style and error checking
- **Black**: Automatic formatting (88 char line length)
- **isort**: Import sorting

### JavaScript/TypeScript (Web Apps)
- **ESLint**: Code style and error checking for both web apps

### General Files
- Remove trailing whitespace
- Ensure files end with newline
- Validate YAML/JSON files
- Prevent large files (>1MB)
- Check for merge conflicts
- Detect private keys

## Usage

### Run Manually
```bash
# Check all files
pre-commit run --all-files

# Check specific hook
pre-commit run flake8-desktop-app
```

### Skip Hooks (Emergency Only!)
```bash
git commit --no-verify -m "Emergency fix"
```

## Fixing Issues

### Python Issues
```bash
cd hidock-desktop-app
# Auto-format
black .
isort .
# Check remaining issues
flake8 .
```

### JavaScript Issues  
```bash
cd hidock-web-app
# Some issues can be auto-fixed
npx eslint . --fix
# Check remaining issues
npm run lint
```

## Troubleshooting

**"No .venv found"**: Run setup script first (`setup-windows.bat` or `setup-unix.sh`)

**"No node_modules found"**: Run `npm install` in the web app directories

**Import order conflicts**: Let isort handle imports - it's configured to work with Black

**ESLint errors**: Many can be auto-fixed with `--fix` flag