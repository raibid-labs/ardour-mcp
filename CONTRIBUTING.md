# Contributing to Ardour MCP

Thank you for your interest in contributing to Ardour MCP! This project aims to bridge professional audio production with AI assistance, and we welcome contributions from developers, musicians, and audio engineers.

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful, inclusive, and constructive in all interactions.

### Our Standards

- **Be respectful**: Treat everyone with respect and consideration
- **Be inclusive**: Welcome newcomers and diverse perspectives
- **Be constructive**: Provide helpful feedback and suggestions
- **Be professional**: Keep discussions focused on the project
- **Be patient**: Remember that everyone is learning

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear, descriptive title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, Ardour version)
- Relevant logs or error messages

### Suggesting Features

Feature suggestions are welcome! Please:
- Check existing issues to avoid duplicates
- Provide clear use cases
- Explain how it benefits users
- Consider implementation complexity

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**: Follow coding standards below
4. **Write tests**: Ensure good test coverage
5. **Run tests**: `uv run pytest`
6. **Format code**: `uv run ruff format src/ tests/`
7. **Lint code**: `uv run ruff check src/ tests/`
8. **Commit changes**: Use clear, descriptive commit messages
9. **Push to your fork**: `git push origin feature/your-feature-name`
10. **Create pull request**: Describe your changes thoroughly

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ardour-mcp.git
cd ardour-mcp

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Format and lint
uv run ruff format src/ tests/
uv run ruff check src/ tests/
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings to all public functions and classes

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When and why this is raised
    """
    pass
```

### Testing

- Write unit tests for all new functionality
- Aim for >80% code coverage
- Use pytest for testing
- Mock external dependencies (OSC, network calls)
- Test both success and error cases

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or tooling changes

Example:
```
feat(transport): Add goto_marker functionality

Implement the goto_marker() MCP tool to allow jumping to named
markers in Ardour sessions. Includes OSC command handling and
state synchronization.

Closes #15
```

## Project Structure

```
ardour-mcp/
├── src/ardour_mcp/     # Main source code
│   ├── server.py       # MCP server implementation
│   ├── osc_bridge.py   # OSC communication layer
│   ├── ardour_state.py # State management
│   └── tools/          # MCP tool implementations
│
├── tests/              # Test suite
│   ├── test_*.py       # Unit tests
│   └── fixtures/       # Test fixtures
│
└── docs/               # Documentation
    ├── ARCHITECTURE.md # System design
    ├── DEVELOPMENT.md  # Developer guide
    └── OSC_API.md     # OSC reference
```

## Documentation

- Update relevant documentation for any changes
- Keep code comments clear and up-to-date
- Add examples for new features
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/)

## Review Process

All pull requests will be reviewed for:
- Code quality and style
- Test coverage
- Documentation completeness
- Adherence to project goals
- Compatibility with Ardour versions

Reviewers may request changes. Please be responsive and collaborative during the review process.

## Getting Help

- **Documentation**: Check [docs/](docs/) folder
- **Issues**: Search existing issues or create new ones
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join project discussions and share ideas

## Recognition

Contributors will be:
- Listed in project documentation
- Mentioned in release notes
- Credited in commit history

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, please:
1. Check existing documentation
2. Search issues and discussions
3. Create a new discussion thread

Thank you for contributing to Ardour MCP! 🎵✨
