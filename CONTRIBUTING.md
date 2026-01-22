# Contributing to Imperva Cloud WAF MCP Server

Thank you for your interest in contributing to the Imperva Cloud WAF MCP Server! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:
1. Check if the issue already exists in the issue tracker
2. If not, create a new issue with a clear title and description
3. Include steps to reproduce for bugs
4. Include use cases and benefits for feature requests

### Contributing Code

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes following our coding standards
4. Write or update tests as needed
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

Before contributing, set up your development environment:

1. Install UV package manager:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Sync project dependencies:
   ```bash
   uv sync
   ```

3. Enable pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

## Coding Standards

### Code Style

This project uses:
- **Black** for code formatting
- **Pylint** for linting

Before submitting code:

1. Format your code with Black:
   ```bash
   python3 -m black --color .
   ```

2. Check code quality with Pylint (minimum score: 8):
   ```bash
   uv run pylint src/ -r y --fail-under=8
   ```

### Code Quality

- Write clear, self-documenting code
- Add docstrings to functions and classes
- Keep functions small and focused
- Follow Python PEP 8 conventions

## Testing

All code contributions must include tests.

### Running Tests

Run the test suite:
```bash
pytest tests/*
```

### Test Requirements

- Write unit tests for new features
- Update existing tests when modifying functionality
- Ensure all tests pass before submitting a PR
- Aim for good test coverage

## Pull Request Process

1. **Update Documentation**: Update README.md if needed for new features
2. **Test Your Changes**: Ensure all tests pass
3. **Code Quality**: Pass Black and Pylint checks
4. **Clear Description**: Write a clear PR description explaining your changes
5. **Link Issues**: Reference any related issues in your PR description

### PR Checklist

Before submitting your pull request:

- [ ] Code follows the project's style guidelines
- [ ] Code has been formatted with Black
- [ ] Pylint score is 8 or higher
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Commit messages are clear and descriptive

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.
