# 🤝 Contributing to HiDock Next

Welcome to HiDock Next! We're excited to have you contribute to our open-source HiDock management platform with AI transcription capabilities.

## 🚀 Quick Start for Contributors

**New contributor?** Get started immediately:

```bash
git clone https://github.com/sgeraldes/hidock-next.git
cd hidock-next
python setup.py
# Choose option 2 (Developer)
```

This automated setup handles everything you need for development.

## 📖 How to Contribute

### 1. 🎯 Areas We Need Help

**High Priority:**
- 🤖 **New AI Providers**: Expand our AI ecosystem beyond the current 11 providers
- 🔧 **Bug Fixes**: Help us squash bugs and improve stability
- 📱 **Mobile Support**: WebUSB mobile compatibility improvements
- 🧪 **Testing**: Increase test coverage across all applications

**Medium Priority:**
- 🎨 **UI/UX Improvements**: Enhance user experience and accessibility
- 📚 **Documentation**: Guides, tutorials, and API documentation
- 🌐 **Internationalization**: Multi-language support
- 🚀 **Performance**: Optimization and efficiency improvements

### 2. 📋 Before You Start

1. **Check existing issues** on [GitHub Issues](https://github.com/sgeraldes/hidock-next/issues)
2. **Join discussions** on [GitHub Discussions](https://github.com/sgeraldes/hidock-next/discussions)
3. **Read our documentation** in the [docs/](docs/) folder
4. **Set up your development environment** using the Quick Start above

### 3. 🛠️ Development Workflow

#### **Step 1: Fork and Clone**
```bash
# Fork the repository on GitHub first
git clone https://github.com/YOUR_USERNAME/hidock-next.git
cd hidock-next
git remote add upstream https://github.com/sgeraldes/hidock-next.git
```

#### **Step 2: Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

#### **Step 3: Make Changes**
- Follow our [Code Quality Standards](#-code-quality-standards)
- Write tests for new functionality
- Update documentation as needed
- Ensure pre-commit hooks pass

#### **Step 4: Test Your Changes**
```bash
# Test desktop app
cd hidock-desktop-app && python -m pytest tests/ -v

# Test web app
cd hidock-web-app && npm test

# Test pre-commit hooks
pre-commit run --all-files
```

#### **Step 5: Commit and Push**
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

#### **Step 6: Create Pull Request**
1. Go to GitHub and create a Pull Request
2. Fill out the PR template completely
3. Link any related issues
4. Wait for review and feedback

## 🎯 Code Quality Standards

### **Line Length**
- **120 characters** for all code (Python, TypeScript, JavaScript)
- Pre-commit hooks enforce this automatically

### **Python Code**
- **Black** formatting with 120-char line length
- **Flake8** linting (E203 slice whitespace exceptions allowed)
- **isort** import sorting with Black profile
- **Type hints** preferred for new code

### **TypeScript/JavaScript Code**
- **ESLint** with React hooks rules
- **TypeScript** strict mode
- **Consistent naming** (camelCase for variables, PascalCase for components)

### **Testing**
- **Unit tests** for all new functions
- **Integration tests** for component interactions
- **Mock data** for external dependencies
- **Test files** have relaxed linting rules

## 📁 Project Structure

```
hidock-next/
├── hidock-desktop-app/     # Python desktop application
├── hidock-web-app/         # React web application
├── audio-insights-extractor/  # Standalone audio analysis tool
├── docs/                   # Project documentation
├── .pre-commit-config.yaml # Code quality hooks
└── setup.py               # Automated setup script
```

## 👥 Types of Contributions

### 🐛 **Bug Reports**
- Use the bug report template
- Include steps to reproduce
- Provide system information
- Add screenshots if helpful

### 💡 **Feature Requests**
- Use the feature request template
- Explain the problem it solves
- Describe your proposed solution
- Consider implementation complexity

### 📝 **Documentation**
- Fix typos and improve clarity
- Add examples and use cases
- Update outdated information
- Create new guides and tutorials

### 🔧 **Code Contributions**
- Follow the development workflow above
- Include tests for new features
- Update documentation as needed
- Follow our coding standards

## 🎮 AI Provider Development

**Want to add a new AI provider?** This is a high-impact contribution!

### Steps to Add a Provider:
1. **Study existing providers** in `hidock-desktop-app/ai_service.py`
2. **Implement the provider class** following the `AIProvider` interface
3. **Add configuration** to settings and UI
4. **Write tests** with mock responses
5. **Update documentation** with setup instructions

### Provider Requirements:
- Support for transcription and/or text analysis
- Error handling and fallback mechanisms
- Secure API key management
- Mock responses for development

## 🌟 Recognition

### **Contributor Hall of Fame**
We recognize significant contributors in our:
- README.md acknowledgments
- Release notes
- Community discussions

### **Contribution Types We Value:**
- 🏆 Major features and architectural improvements
- 🔧 Bug fixes and stability improvements
- 📚 Documentation and tutorial creation
- 🧪 Test coverage and quality improvements
- 🎨 UI/UX enhancements
- 🌐 Accessibility and internationalization

## 📞 Getting Help

### **Before Contributing:**
1. **Read the docs**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
2. **Check existing issues**: Avoid duplicating work
3. **Ask questions**: Use GitHub Discussions

### **During Development:**
1. **Pre-commit hook issues**: See [docs/PRE-COMMIT.md](docs/PRE-COMMIT.md)
2. **Setup problems**: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. **AI development**: Use [AGENT.md](AGENT.md) for Claude Code assistance

### **Need Help?**
- 💬 **Questions**: [GitHub Discussions](https://github.com/sgeraldes/hidock-next/discussions)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/sgeraldes/hidock-next/issues)
- 📧 **Direct Contact**: Create an issue and we'll respond

## 📜 Code of Conduct

### **Our Standards**
- **Be respectful** and inclusive
- **Be constructive** in feedback
- **Be patient** with new contributors
- **Be collaborative** and helpful

### **Unacceptable Behavior**
- Harassment or discrimination
- Trolling or inflammatory comments
- Publishing private information
- Unprofessional conduct

## 📄 License

By contributing to HiDock Next, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

## 🚀 Ready to Contribute?

1. **⭐ Star** this repository
2. **🍴 Fork** the project
3. **📋 Pick** an issue or feature
4. **💻 Code** your contribution
5. **🔄 Submit** a pull request

**Thank you for making HiDock Next better! 🎉**

---

*For detailed technical information, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)*
