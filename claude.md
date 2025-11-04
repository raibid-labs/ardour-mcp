# Claude.md - AI Assistant Context for Ardour MCP

This file provides context for AI assistants (like Claude) when working with the Ardour MCP codebase.

## Project Overview

**Ardour MCP** is a Model Context Protocol (MCP) server that enables AI assistants to control Ardour, a professional open-source Digital Audio Workstation (DAW). This is the first MCP integration for a major open-source DAW.

## Core Concepts

### What is Ardour?
Ardour is a professional, open-source DAW for recording, editing, and mixing audio. It's used by musicians, audio engineers, and producers worldwide.

### What is MCP?
The Model Context Protocol is a standardized way for AI assistants to interact with external tools and services. It defines how tools are exposed and called.

### What is OSC?
Open Sound Control (OSC) is a network protocol for communication between computers, sound synthesizers, and multimedia devices. Ardour uses OSC for remote control.

## Architecture

The system has three main layers:

1. **MCP Server Layer** (`server.py`)
   - Exposes tools to AI assistants via MCP protocol
   - Handles tool registration and execution
   - Manages error handling and responses

2. **OSC Bridge Layer** (`osc_bridge.py`)
   - Sends OSC commands to Ardour
   - Receives OSC feedback from Ardour
   - Manages bidirectional communication

3. **State Management Layer** (`ardour_state.py`)
   - Caches Ardour's current state from OSC feedback
   - Provides quick access to session information
   - Reduces need for round-trip queries

## Key Files and Their Purpose

### Source Code (`src/ardour_mcp/`)

- **`server.py`**: Main MCP server, tool registration
- **`osc_bridge.py`**: OSC communication with Ardour (TODO)
- **`ardour_state.py`**: State caching and management (TODO)
- **`tools/`**: Individual MCP tool implementations
  - `transport.py`: Play, stop, record, navigation (TODO)
  - `tracks.py`: Track creation, selection, management (TODO)
  - `session.py`: Session info queries (TODO)
  - `recording.py`: Recording controls (TODO)

### Documentation (`docs/`)

- **`ARCHITECTURE.md`**: Detailed system design
- **`DEVELOPMENT.md`**: Developer setup and workflow
- **`OSC_API.md`**: Complete Ardour OSC command reference
- **`ROADMAP.md`**: Feature timeline and milestones

### Configuration

- **`pyproject.toml`**: Python project configuration, dependencies
- **`.gitignore`**: Git ignore patterns
- **`CHANGELOG.md`**: Version history

## Development Workflow

### Setting Up

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check src/ tests/
```

### Testing Philosophy

- **Unit tests**: Test individual components in isolation
- **Mock external dependencies**: Use mocks for OSC, network calls
- **Test success and error cases**: Ensure robust error handling
- **Aim for >80% coverage**: Maintain high test quality

### Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Add docstrings to all public functions/classes
- Use descriptive names

## Current Development Phase

**Phase 1 (MVP) - January-February 2025**

Focus areas:
1. OSC communication bridge (Issue #1)
2. State management system (Issue #2)
3. Core MCP tools (Issues #3-5)
4. Basic testing infrastructure

## Common Tasks

### Adding a New MCP Tool

1. Create module in `src/ardour_mcp/tools/`
2. Implement tool function with proper typing
3. Add docstring with MCP tool description
4. Register tool in `server.py`
5. Write unit tests
6. Update documentation

### Working with OSC

Key OSC concepts:
- **Commands**: Sent to Ardour (e.g., `/transport_play`)
- **Feedback**: Received from Ardour (e.g., `/transport_frame`)
- **Address patterns**: OSC paths like `/strip/1/gain`
- **Type tags**: OSC data types (i=int, f=float, s=string)

### Testing OSC Code

```python
from unittest.mock import Mock, patch

def test_transport_play():
    # Mock the OSC bridge
    with patch('ardour_mcp.osc_bridge.ArdourOSCBridge') as mock_bridge:
        # Set up mock behavior
        mock_bridge.send_command.return_value = True

        # Test the tool
        result = transport_play()

        # Verify OSC command was sent
        mock_bridge.send_command.assert_called_with('/transport_play')
```

## Important Considerations

### Error Handling

- Always validate inputs before sending OSC commands
- Handle network failures gracefully
- Provide clear error messages to users
- Log errors for debugging

### Performance

- Use state cache to avoid unnecessary OSC queries
- Batch multiple operations when possible
- Handle OSC feedback asynchronously
- Don't block on network operations

### Compatibility

- Support Ardour 8.x (latest stable)
- Test with different Ardour configurations
- Handle missing or disabled features gracefully
- Document version-specific behavior

## Resources for Development

### Ardour
- [Ardour Manual](https://manual.ardour.org/)
- [OSC Documentation](https://manual.ardour.org/using-control-surfaces/controlling-ardour-with-osc/)
- [Ardour Source Code](https://github.com/Ardour/ardour)

### MCP
- [MCP Specification](https://modelcontextprotocol.io/)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Example Servers](https://github.com/modelcontextprotocol/servers)

### Python/OSC
- [python-osc Documentation](https://python-osc.readthedocs.io/)
- [OSC Specification](http://opensoundcontrol.org/spec-1_0)

## Tips for AI Assistants

When helping with this codebase:

1. **Check existing documentation first**: Most design decisions are documented
2. **Follow the architecture**: Don't bypass layers (e.g., tools → state → OSC bridge → Ardour)
3. **Maintain consistency**: Follow existing patterns for new features
4. **Test thoroughly**: Audio software requires reliability
5. **Consider latency**: Real-time audio requires responsive controls
6. **Document assumptions**: Audio engineering context may not be obvious

## Questions to Ask

If uncertain about implementation:
- What is the expected latency for this operation?
- Does this need to be synchronous or can it be async?
- How should we handle Ardour being unavailable?
- What feedback should the user receive?
- Are there version-specific considerations?

## Project Goals

1. **Accessibility**: Make professional audio production more accessible through AI assistance
2. **Reliability**: Build a robust, production-ready tool
3. **Community**: Foster collaboration between audio and AI communities
4. **Innovation**: Pioneer AI integration in open-source audio software
5. **Education**: Help people learn audio production through AI assistance

---

This context should help AI assistants understand the project structure, development workflow, and key considerations when working with the Ardour MCP codebase.
