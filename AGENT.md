# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HiDock Next is a multi-platform application suite for managing HiDock recording devices locally with comprehensive AI-powered transcription and analysis capabilities. The project includes three main applications:

- **Desktop Application** (Python): Full-featured GUI application with 11 AI provider support

## Architecture

### Desktop Application (`hidock-desktop-app/`)

The desktop application is the flagship component with advanced AI integration and professional-grade features.

#### Core Architecture

- **Main Entry**: `main.py` - Application entry point with enhanced error handling
- **Device Communication**:
  - `hidock_device.py` - USB device interface using pyusb/libusb
  - `enhanced_device_selector.py` - Professional device selection UI with status indicators
- **Configuration**: `config_and_logger.py` - Centralized config and logging with encryption support
- **File Operations**: `file_operations_manager.py` - Local file management with HTA conversion support

#### AI Integration Layer

- **Unified AI Service**: `ai_service.py` - Central service managing 11 AI providers
  - **Cloud Providers**: Google Gemini, OpenAI, Anthropic, OpenRouter, Amazon Bedrock, Qwen, DeepSeek
  - **Local Providers**: Ollama, LM Studio
  - **Mock Providers**: Development and testing support
- **Transcription Module**: `transcription_module.py` - Multi-provider audio transcription and analysis
- **HTA Converter**: `hta_converter.py` - Proprietary audio format conversion utility

#### Advanced Features

- **Background Processing**: Non-blocking AI operations with progress tracking and cancellation
- **Security**: Encrypted API key storage using Fernet encryption
- **File Format Support**: Native .hda, .hta conversion, standard audio formats

## Quick Setup

**Get started immediately with the automated setup:**

```bash
# For end users (just run the apps):
python setup.py  # Choose option 1

# For developers (contribute code):
python setup.py  # Choose option 2
```

**Or use platform-specific scripts:**

```bash
# Windows (double-click):
setup-windows.bat

# Linux/Mac:
chmod +x setup-unix.sh && ./setup-unix.sh
```

## Common Development Commands

### Desktop Application

```bash
cd hidock-desktop-app

# Activate environment (after setup)
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Run the application
python main.py

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html

# Code formatting and linting
black .
flake8 .
isort .
mypy .
```

## Key Configuration Files

- **Python**: `hidock-desktop-app/pyproject.toml` - Project metadata, dependencies, and tool configuration
- **Desktop Config**: `hidock-desktop-app/hidock_config.json` - Runtime application settings
- **Test Configuration**: `hidock-desktop-app/pytest.ini` - Python test settings and markers

## Development Workflow

### Testing Strategy

- **Python**: pytest with markers for unit (`@pytest.mark.unit`), integration (`@pytest.mark.integration`), and device tests (`@pytest.mark.device`)
- **Coverage**: Minimum 80% coverage required for Python code

### Code Style

- **Python**: Black formatter (line length 88), Flake8 linting, isort for imports, mypy for type checking

### Git Workflow

- Main branch: `main` (production-ready)
- Feature branches: `feature/feature-name`
- Bug fixes: `bugfix/bug-description`
- Conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`

## Device Communication

### USB Protocol

- **Desktop**: Direct USB communication via pyusb/libusb
- **Device Types**: HiDock H1, H1E, P1 variants
- **Operations**: List recordings, download, play, delete, format storage, sync time

### File Formats

- **Audio**: `.hda`, `.hta` (HiDock proprietary formats), `.wav`, `.mp3`, `.flac`, `.m4a`
- **Conversion**:
  - **HTA Converter**: Proprietary format to WAV conversion
  - **Audio Processing**: pygame for playback, matplotlib for visualization
- **Storage**: Local downloads to user-configured directory with automatic conversion

## AI Integration

### Desktop Application - Multi-Provider Support

The desktop application supports **7 implemented AI providers** with **3 additional providers planned** through a unified interface:

#### Fully Implemented Providers (7)

- **Google Gemini**: Complete implementation with multiple models (gemini-1.5-flash, gemini-pro)
- **OpenAI**: Full GPT and Whisper integration for transcription and analysis
- **Anthropic**: Claude models for text analysis
- **OpenRouter**: Multi-provider access through single API
- **Ollama**: Local model serving with LLaMA, Mistral, CodeLlama support
- **LM Studio**: GGUF model hosting with OpenAI-compatible API
- **Mock Provider**: For development and testing without API keys

#### Planned/Future Providers (3)

- **Amazon Bedrock**: Enterprise AI models (referenced in imports, not implemented)
- **Qwen**: Alibaba's multilingual models (mentioned in comments, not implemented)
- **DeepSeek**: Coding-specialized models (mentioned in comments, not implemented)

#### Features

- **Unified Interface**: Single API for all providers through `ai_service.py`
- **Secure Storage**: Encrypted API key management with Fernet encryption
- **Provider Abstraction**: Abstract base class ensures consistent interfaces
- **Mock Support**: Development and testing without API keys
- **Background Processing**: Non-blocking transcription with progress tracking
- **Error Handling**: Comprehensive error reporting and fallback mechanisms

## Dependencies

### Python (Desktop)

#### Core Dependencies

- `pyusb` - USB device communication with libusb backend
- `matplotlib` - Real-time audio visualization and waveform display
- `cryptography` - Secure API key encryption with Fernet

#### AI Provider Dependencies

- `google-generativeai` - Google Gemini integration
- `openai` - OpenAI GPT and Whisper integration
- `anthropic` - Anthropic Claude integration
- `boto3` - Amazon Bedrock integration (optional)
- `requests` - HTTP client for OpenRouter, Ollama, LM Studio, other providers

#### Development Tools

- `pytest` - Testing framework with coverage reporting
- `black` - Code formatting (line length 88)
- `flake8` - Linting and style checking
- `isort` - Import sorting and organization
- `mypy` - Static type checking

## Important Notes

### Desktop Application

- Always run from the `hidock-desktop-app/` directory to ensure proper icon and configuration file paths
- **AI Provider Setup**: Each provider requires specific configuration in settings
- **Local Models**: Ollama and LM Studio require separate server installation
- **API Keys**: Stored encrypted in `hidock_config.json` - never commit plain text keys
- **HTA Files**: Automatically converted to WAV for AI processing
- **Background Processing**: Use progress bars and cancellation for long AI operations

### Development Guidelines

- **Testing**: Device tests require actual HiDock hardware (`@pytest.mark.device`)
- **AI Testing**: Mock providers available for development without API keys
- **Error Handling**: Always implement fallback mechanisms for AI operations
- **Configuration**: JSON format with validation before commits
- **Security**: Never log or expose API keys in debug output

### Multi-Provider AI Architecture

- **Provider Registration**: Use `ai_service.configure_provider()` before operations
- **Unified Interface**: All providers implement `AIProvider` abstract base class
- **Error Handling**: Providers return consistent error response format
- **Mock Development**: Set empty API keys to trigger mock responses for testing
