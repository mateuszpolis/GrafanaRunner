# Contributing to Grafana Runner

Thank you for your interest in contributing to Grafana Runner! This document provides guidelines and instructions for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Git
- Chrome or Firefox browser

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/grafana-runner.git
   cd grafana-runner
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

## 📝 Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) for consistent commit messages and automatic versioning.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to our CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Examples

```bash
# Feature
feat: add support for Firefox browser in kiosk mode

# Bug fix
fix: resolve Chrome crash on Windows 11

# Documentation
docs: update installation instructions for Windows

# Breaking change
feat!: change configuration file format to YAML

# With scope
feat(ui): add progress indicator for panel loading
```

### Breaking Changes

Breaking changes must be indicated by:
1. `!` after the type/scope: `feat!: change API`
2. Or in the footer: `BREAKING CHANGE: explanation`

## 🔄 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- Follow the existing code style (enforced by Black and flake8)
- Add tests for new functionality
- Update documentation as needed
- Ensure all pre-commit hooks pass

### 3. Test Your Changes

```bash
# Run code quality checks
black .
isort .
flake8 .

# Run tests
pytest

# Test the application
python grafana_runner.py
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add your new feature"
```

The pre-commit hooks will automatically:
- Format code with Black
- Sort imports with isort
- Run linting with flake8
- Validate commit message format

### 5. Push and Create Pull Request

```bash
git push origin your-branch-name
```

Then create a pull request through GitHub.

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=grafana_runner

# Run specific test file
pytest tests/test_specific.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure scenarios
- Mock external dependencies (browsers, network calls)

## 📋 Code Quality

### Automated Checks

The project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **bandit**: Security scanning
- **pre-commit**: Git hooks

### Manual Code Review Checklist

- [ ] Code follows existing patterns and conventions
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] No sensitive information is committed
- [ ] Performance impact is considered

## 🏷️ Versioning and Releases

Versions are automatically determined based on commit messages:

- **Major version** (`X.0.0`): Breaking changes (`feat!:` or `BREAKING CHANGE:`)
- **Minor version** (`0.X.0`): New features (`feat:`)
- **Patch version** (`0.0.X`): Bug fixes (`fix:`)

Releases are automatically created when commits are pushed to the `main` branch.

## 📚 Documentation

### Updating Documentation

- Update `README.md` for user-facing changes
- Update docstrings for code changes
- Update `CHANGELOG.md` (automatically generated)

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Use emojis to improve readability
- Keep installation instructions up-to-date

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Environment details**: OS, Python version, browser version
2. **Configuration**: Sanitized `config.json` (remove sensitive URLs)
3. **Steps to reproduce**: Clear, step-by-step instructions
4. **Expected vs actual behavior**: What should happen vs what happens
5. **Logs**: Relevant log output from `grafana_runner.log`

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume positive intent

### Unacceptable Behavior

- Harassment or discrimination
- Offensive language or imagery
- Personal attacks
- Spam or trolling

## 📞 Getting Help

- 💬 **Discussions**: Use GitHub Discussions for questions
- 🐛 **Issues**: Use GitHub Issues for bugs and feature requests
- 📧 **Security**: Email security issues privately

## 🎉 Recognition

Contributors will be recognized in:
- The project's README
- Release notes
- GitHub contributors page

Thank you for contributing to Grafana Runner! 🚀
