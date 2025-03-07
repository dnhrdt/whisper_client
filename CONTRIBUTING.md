# Contributing to WhisperClient
Version: 1.0
Timestamp: 2025-03-08 00:12 CET

Thank you for your interest in contributing to WhisperClient! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

## Code of Conduct

We expect all contributors to:
- Be respectful and inclusive in communications
- Accept constructive criticism gracefully
- Focus on what is best for the community and project
- Show empathy towards other community members

## Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/dnhrdt/whisper_client.git
   cd whisper_client
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set Up WhisperLive Server**
   - Follow the instructions at [WhisperLive](https://github.com/collabora/WhisperLive) to set up the server
   - Configure the server URL in `config.json`

5. **Configure Audio Device**
   - Use `python list_devices.py` to find your audio device
   - Update `config.json` with your device name

## Coding Standards

We follow PEP 8 conventions with a few project-specific guidelines:

1. **Code Style**
   - Use 4 spaces for indentation (no tabs)
   - Maximum line length of 100 characters
   - Use descriptive variable and function names
   - Add type hints to function signatures (Python 3.12+)

2. **Documentation**
   - All functions, classes, and modules must have docstrings
   - Follow Google-style docstring format
   - Keep docstrings up-to-date with code changes

3. **Error Handling**
   - Use structured error handling with specific exception types
   - Log errors with appropriate context
   - Provide meaningful error messages

4. **Line Endings**
   - Python files use LF (*.py)
   - Documentation files use LF (*.md, *.txt, *.json)
   - Windows scripts use CRLF (*.bat, *.cmd, *.ps1)

5. **Commit Messages**
   - Format: `<type>(<scope>): <description>`
   - Types: feat, fix, docs, style, refactor, test, chore
   - Keep descriptions clear and concise
   - Reference issue numbers when applicable

## Pull Request Process

1. **Create a Branch**
   - Create a branch from `main` with a descriptive name
   - Use prefixes like `feature/`, `fix/`, `docs/`, etc.
   - Example: `feature/improve-audio-processing`

2. **Make Your Changes**
   - Follow the coding standards
   - Keep changes focused on a single issue
   - Write tests for new features or bug fixes
   - Update documentation as needed

3. **Test Your Changes**
   - Run the existing test suite: `python run_tests.py`
   - Add new tests for your changes
   - Verify that all tests pass

4. **Submit a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Fill out the pull request template
   - Request review from maintainers

5. **Address Review Feedback**
   - Be responsive to review comments
   - Make requested changes promptly
   - Discuss any disagreements respectfully
   - Update your PR as needed

## Issue Reporting

When reporting issues, please include:

1. **Environment Information**
   - Operating system version
   - Python version
   - Audio device being used
   - Application where text is being inserted

2. **Issue Details**
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs. actual behavior
   - Relevant log entries (from logs/whisper_client_*.log)

3. **Performance Metrics (if applicable)**
   - CPU usage
   - Memory consumption
   - Response time
   - Transcription accuracy

## Testing Requirements

1. **Types of Tests**
   - Unit tests for individual components
   - Integration tests for component interactions
   - Timing tests for performance analysis
   - Speech tests for transcription accuracy

2. **Test Coverage**
   - Aim for at least 80% code coverage
   - Critical components should have 100% coverage
   - Edge cases should be thoroughly tested

3. **Running Tests**
   ```bash
   # Run all tests
   python run_tests.py
   
   # Run specific test categories
   python run_tests.py --category timing
   python run_tests.py --category integration
   python run_tests.py --category speech
   ```

4. **Test Documentation**
   - Document test purpose and methodology
   - Explain test setup and dependencies
   - Document expected outcomes

## Documentation

1. **Memory Bank Structure**
   - All documentation follows the Memory Bank structure
   - Update relevant Memory Bank files with changes
   - Ensure version and timestamp are updated

2. **Documentation Files**
   - Update README.md for user-facing changes
   - Update technical documentation for implementation details
   - Create new documentation for new features

3. **Documentation Standards**
   - Clear and concise language
   - Code examples where appropriate
   - Diagrams for complex concepts
   - Consistent formatting and style

Thank you for contributing to WhisperClient! Your efforts help make this project better for everyone.
