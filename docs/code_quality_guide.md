# Code Quality Guide
Version: 1.0
Timestamp: 2025-03-08 22:13 CET

This document provides comprehensive guidance on maintaining code quality in the WhisperClient project. It explains the tools we use, how to set them up, and how to run them effectively.

## Table of Contents
- [Introduction](#introduction)
- [Development Environment Setup](#development-environment-setup)
- [Code Quality Tools](#code-quality-tools)
- [Running Code Quality Checks](#running-code-quality-checks)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Introduction

Maintaining high code quality is essential for the long-term success of the WhisperClient project. We use a variety of tools to ensure that our code is clean, consistent, and maintainable. This guide will help you understand and use these tools effectively.

## Development Environment Setup

### Prerequisites
- Python 3.12+
- Virtual environment (venv)

### Setting Up Your Environment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/dnhrdt/whisper_client.git
   cd whisper_client
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   .\venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Install project dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Code Quality Tools

We use the following tools to maintain code quality:

### 1. Pylint

Pylint is a static code analyzer that looks for programming errors, helps enforce a coding standard, and looks for code smells.

**Configuration**: `.pylintrc`

**Key Features**:
- Checks for errors and enforces coding standards
- Provides suggestions for code improvement
- Customizable through configuration file

### 2. Black

Black is an uncompromising code formatter that formats your code in a consistent style.

**Configuration**: `pyproject.toml` (under `[tool.black]`)

**Key Features**:
- Automatic code formatting
- Consistent style across the project
- Minimal configuration required

### 3. isort

isort is a utility to sort imports alphabetically and automatically separate them into sections.

**Configuration**: `pyproject.toml` (under `[tool.isort]`)

**Key Features**:
- Sorts imports alphabetically
- Separates imports into sections
- Formats imports consistently

### 4. flake8

flake8 is a wrapper around PyFlakes, pycodestyle, and McCabe complexity.

**Configuration**: `.pre-commit-config.yaml`

**Key Features**:
- Checks for syntax errors
- Enforces PEP 8 style guide
- Checks for code complexity

### 5. mypy

mypy is an optional static type checker for Python.

**Configuration**: `pyproject.toml` (under `[tool.mypy]`)

**Key Features**:
- Checks type annotations
- Helps catch type-related errors
- Improves code documentation

### 6. pre-commit

pre-commit is a framework for managing and maintaining multi-language pre-commit hooks.

**Configuration**: `.pre-commit-config.yaml`

**Key Features**:
- Runs checks before each commit
- Prevents committing code with issues
- Integrates multiple tools

## Running Code Quality Checks

### Using Pre-commit

Pre-commit runs all configured hooks automatically when you commit code. You can also run it manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files src/file.py

# Run specific hook
pre-commit run black --all-files
```

### Running Tools Individually

#### Pylint

```bash
# Check a specific file
pylint src/file.py

# Check a directory
pylint src/

# Generate a report
pylint src/ --output=pylint_report.txt
```

#### Black

```bash
# Format a specific file
black src/file.py

# Format a directory
black src/

# Check formatting without making changes
black --check src/
```

#### isort

```bash
# Sort imports in a specific file
isort src/file.py

# Sort imports in a directory
isort src/

# Check import sorting without making changes
isort --check src/
```

#### flake8

```bash
# Check a specific file
flake8 src/file.py

# Check a directory
flake8 src/
```

#### mypy

```bash
# Type check a specific file
mypy src/file.py

# Type check a directory
mypy src/
```

### VS Code Integration

VS Code can automatically run these tools when you save files. Our recommended settings are:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Continuous Integration

We use GitHub Actions to run code quality checks on every pull request and push to the main branch. The configuration is in `.github/workflows/code-quality.yml`.

The CI pipeline runs:
- Pylint
- Black
- isort
- flake8
- mypy
- pytest with coverage

## Troubleshooting

### Common Issues

#### 1. Pre-commit Hooks Failing

If pre-commit hooks are failing, you can:
- Run `pre-commit run --all-files` to see the issues
- Fix the issues manually
- Run the specific tool that's failing to get more detailed output

#### 2. Conflicting Formatting Rules

If you encounter conflicts between different tools:
- Black takes precedence over other formatting tools
- Configure isort to be compatible with Black using `profile = "black"`
- Disable conflicting rules in Pylint or flake8

#### 3. False Positives

If you encounter false positives:
- Add inline comments to disable specific checks: `# pylint: disable=rule-code`
- Update the configuration files to disable specific rules globally
- Document why you're disabling a rule

## Best Practices

### 1. Code Style

- Follow PEP 8 conventions
- Use descriptive variable and function names
- Add type hints to function signatures
- Keep functions and methods small and focused
- Use docstrings for all functions, classes, and modules

### 2. Documentation

- Keep docstrings up-to-date with code changes
- Follow Google-style docstring format
- Document complex algorithms and decisions
- Update documentation when you change code

### 3. Testing

- Write tests for all new features
- Maintain high test coverage
- Run tests locally before committing
- Use pytest fixtures for test setup

### 4. Workflow

- Run code quality checks before committing
- Address all issues before submitting a pull request
- Review code quality reports in CI
- Continuously improve code quality

## Conclusion

By following this guide and using the provided tools, you'll help maintain high code quality in the WhisperClient project. This will make the codebase more maintainable, reduce bugs, and improve the developer experience for everyone.

If you have questions or suggestions about code quality, please open an issue or discuss it with the team.
