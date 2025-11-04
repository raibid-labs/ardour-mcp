# Development Guide

This guide covers setting up a development environment, development workflow, testing, and contribution guidelines for Ardour MCP.

## Prerequisites

### Required Software

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **uv**: Fast Python package manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Ardour 8.x**: [Download Ardour](https://ardour.org/download.html)
- **Git**: Version control

### Recommended Software

- **VS Code** or **PyCharm**: IDE with Python support
- **Claude Desktop**: For testing MCP integration
- **OSC testing tools**: osculator, OSCTest, or similar

## Setting Up Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/raibid-labs/ardour-mcp.git
cd ardour-mcp
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev dependencies
uv sync --all-extras

# Or if you prefer using pip
pip install -e ".[dev]"
```

### 3. Configure Ardour

#### Enable OSC in Ardour

1. Launch Ardour
2. **Edit → Preferences → Control Surfaces**
3. Enable **Open Sound Control (OSC)**
4. Configure:
   - **Port**: 3819 (default)
   - **Feedback**: Enable all feedback options
   - **Bank Size**: 0 (unlimited)
5. Click **OK** and restart Ardour

#### Verify OSC Connection

```bash
# Test OSC connectivity (requires python-osc)
python -c "from pythonosc import udp_client; client = udp_client.SimpleUDPClient('127.0.0.1', 3819); client.send_message('/transport_stop', []); print('Command sent!')"
```

### 4. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/ardour_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_osc_bridge.py

# Run specific test
uv run pytest tests/test_osc_bridge.py::test_send_command
```

### 5. Run the MCP Server

```bash
# Run in development mode
uv run ardour-mcp

# Run with debug logging
LOG_LEVEL=DEBUG uv run ardour-mcp
```

## Development Workflow

### Code Organization

```
src/ardour_mcp/
├── __init__.py           # Package initialization
├── server.py             # Main MCP server
├── osc_bridge.py         # OSC communication layer
├── ardour_state.py       # State management
└── tools/                # MCP tool implementations
    ├── __init__.py       # Tool registration
    ├── transport.py      # Transport controls
    ├── tracks.py         # Track management
    ├── session.py        # Session information
    └── recording.py      # Recording controls
```

### Adding a New Tool

1. **Create tool module** in `src/ardour_mcp/tools/`:

```python
# tools/my_tool.py
from typing import Optional

async def my_tool(param1: str, param2: int) -> dict:
    """
    Brief description of what this tool does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Dictionary with results

    Raises:
        ValueError: When inputs are invalid
    """
    # Validate inputs
    if param2 < 0:
        raise ValueError("param2 must be non-negative")

    # Implementation
    # ...

    return {"success": True, "result": "..."}
```

2. **Register tool** in `server.py`:

```python
from ardour_mcp.tools.my_tool import my_tool

# In server initialization
server.register_tool(
    "my_tool",
    "Brief description for AI assistant",
    {
        "param1": {"type": "string", "description": "..."},
        "param2": {"type": "integer", "description": "..."}
    },
    my_tool
)
```

3. **Write tests** in `tests/test_my_tool.py`:

```python
import pytest
from ardour_mcp.tools.my_tool import my_tool

def test_my_tool_success():
    result = await my_tool("test", 42)
    assert result["success"] == True

def test_my_tool_invalid_input():
    with pytest.raises(ValueError):
        await my_tool("test", -1)
```

4. **Update documentation**:
   - Add to README.md feature list
   - Document OSC commands in OSC_API.md
   - Update CHANGELOG.md

### Code Style

#### Formatting

We use **Ruff** for formatting and linting:

```bash
# Format code
uv run ruff format src/ tests/

# Check formatting
uv run ruff format --check src/ tests/

# Lint code
uv run ruff check src/ tests/

# Fix linting issues automatically
uv run ruff check --fix src/ tests/
```

#### Style Guidelines

- **Line length**: Maximum 100 characters
- **Imports**: Sorted with isort rules
- **Type hints**: All function signatures must have type hints
- **Docstrings**: All public functions and classes
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

#### Example Function

```python
def set_track_volume(track_id: int, volume_db: float) -> dict[str, any]:
    """
    Set the volume of a track in Ardour.

    Args:
        track_id: The track number (1-based)
        volume_db: Volume in decibels (-inf to +6dB typically)

    Returns:
        Dictionary with 'success' boolean and optional 'error' message

    Raises:
        ValueError: If track_id is invalid or volume_db is out of range
    """
    # Validate inputs
    if track_id < 1:
        raise ValueError(f"Invalid track_id: {track_id}")
    if volume_db < -144 or volume_db > 6:
        raise ValueError(f"Volume out of range: {volume_db}dB")

    # Send OSC command
    osc_bridge.send_command(f"/strip/gain/{track_id}", volume_db)

    return {"success": True}
```

### Testing

#### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_osc_bridge.py       # OSC bridge tests
├── test_ardour_state.py     # State management tests
├── test_transport.py        # Transport tool tests
└── fixtures/
    └── mock_ardour.py       # Mock Ardour OSC server
```

#### Writing Tests

**Use pytest fixtures for setup**:

```python
@pytest.fixture
def mock_osc_bridge():
    """Provide a mock OSC bridge for testing."""
    bridge = Mock(spec=ArdourOSCBridge)
    bridge.send_command.return_value = True
    return bridge

def test_transport_play(mock_osc_bridge):
    result = transport_play(mock_osc_bridge)
    mock_osc_bridge.send_command.assert_called_with('/transport_play')
    assert result["success"] == True
```

**Test both success and failure cases**:

```python
def test_set_volume_success():
    result = set_track_volume(1, -6.0)
    assert result["success"] == True

def test_set_volume_invalid_track():
    with pytest.raises(ValueError, match="Invalid track_id"):
        set_track_volume(0, -6.0)

def test_set_volume_out_of_range():
    with pytest.raises(ValueError, match="Volume out of range"):
        set_track_volume(1, 100.0)
```

**Mock external dependencies**:

```python
@patch('ardour_mcp.osc_bridge.SimpleUDPClient')
def test_osc_bridge_connection(mock_client):
    bridge = ArdourOSCBridge()
    bridge.connect()
    mock_client.assert_called_with('127.0.0.1', 3819)
```

#### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/ardour_mcp --cov-report=term-missing

# Run specific tests
uv run pytest tests/test_transport.py
uv run pytest tests/test_transport.py::test_transport_play

# Run tests matching pattern
uv run pytest -k "test_volume"

# Show print statements
uv run pytest -s

# Stop on first failure
uv run pytest -x

# Run in parallel (requires pytest-xdist)
uv run pytest -n auto
```

## Debugging

### Logging

Configure logging for debugging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### OSC Debugging

Monitor OSC traffic with `oscdump`:

```bash
# Install osctools
pip install python-osc

# Monitor OSC messages
python -c "from pythonosc import dispatcher, osc_server; d = dispatcher.Dispatcher(); d.set_default_handler(print); server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', 3820), d); print('Listening on port 3820...'); server.serve_forever()"
```

### Common Issues

**Issue: "Cannot connect to Ardour"**
- Verify Ardour is running
- Check OSC is enabled in Preferences
- Verify port number (default: 3819)
- Check firewall settings

**Issue: "No feedback received"**
- Enable feedback in Ardour OSC settings
- Check feedback port (default: 3820)
- Verify network connectivity

**Issue: "Import errors"**
- Run `uv sync --all-extras`
- Check virtual environment is activated
- Verify Python version >= 3.8

## Contributing

### Workflow

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make changes** following style guide
4. **Write tests** for new functionality
5. **Run tests**: `uv run pytest`
6. **Format code**: `uv run ruff format src/ tests/`
7. **Lint code**: `uv run ruff check src/ tests/`
8. **Commit changes**: Follow commit message guidelines
9. **Push to fork**: `git push origin feature/my-feature`
10. **Create pull request** on GitHub

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, whitespace)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

**Example:**

```
feat(transport): Add goto_marker functionality

Implement goto_marker() tool to jump to named markers in Ardour
sessions. Includes OSC command handling and state synchronization.

Closes #15
```

### Pull Request Guidelines

- **Clear title and description**
- **Link related issues**
- **Include tests** for new features
- **Update documentation**
- **Pass all CI checks**
- **Respond to review feedback**

## IDE Setup

### VS Code

**Recommended extensions:**
- Python (Microsoft)
- Pylance
- Ruff
- GitLens

**Settings (.vscode/settings.json):**

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.linting.enabled": true,
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

1. **Set Python interpreter**: Preferences → Project → Python Interpreter → Add (.venv)
2. **Enable pytest**: Preferences → Tools → Python Integrated Tools → Testing: pytest
3. **Configure Ruff**: Preferences → Tools → External Tools → Add Ruff

## Resources

### Documentation

- [Ardour Manual](https://manual.ardour.org/)
- [Ardour OSC Docs](https://manual.ardour.org/using-control-surfaces/controlling-ardour-with-osc/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Python OSC Library](https://python-osc.readthedocs.io/)

### Community

- [GitHub Issues](https://github.com/raibid-labs/ardour-mcp/issues)
- [GitHub Discussions](https://github.com/raibid-labs/ardour-mcp/discussions)
- [Ardour Forums](https://discourse.ardour.org/)

## Getting Help

1. **Check documentation** in `docs/` folder
2. **Search existing issues** on GitHub
3. **Ask in Discussions** for questions
4. **Create an issue** for bugs or feature requests

---

Happy coding! 🎵💻
