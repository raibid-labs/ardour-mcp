# Ardour MCP 🎵

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Server-green.svg)](https://modelcontextprotocol.io/)

**Model Context Protocol server for Ardour DAW - Control Ardour through AI assistants**

The first MCP integration for a major open-source Digital Audio Workstation. Ardour MCP enables natural language control of [Ardour](https://ardour.org/) through AI assistants like Claude, using the [Model Context Protocol](https://modelcontextprotocol.io/).

## 🎯 What This Does

Ardour MCP allows you to control Ardour using natural language:

- **"Start playback in Ardour"** → Transport control
- **"Create a new audio track called 'Vocals'"** → Track management
- **"Set track 1 volume to -6dB"** → Mixer operations
- **"What's the current session tempo?"** → Session information queries
- **"Arm track 2 for recording"** → Recording setup

## ✨ Features

### Phase 1 (MVP) - In Development

- 🎮 **Transport Control**: Play, stop, record, navigation
- 📊 **Session Information**: Query tempo, sample rate, track count
- 🎚️ **Track Management**: Create, select, rename tracks
- 🎛️ **Basic Mixer**: Volume, pan, mute, solo controls
- 📝 **Markers**: Create and navigate to session markers

### Planned Features

See [ROADMAP.md](docs/ROADMAP.md) for complete feature timeline:
- Advanced mixer operations (sends, inserts, automation)
- Plugin control and management
- Region editing and manipulation
- Snapshot and template management
- And much more!

## 🚀 Quick Start

### Prerequisites

- **Ardour 8.x** with OSC enabled
- **Python 3.8+**
- **uv** package manager (recommended)

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/raibid-labs/ardour-mcp.git
cd ardour-mcp

# Install dependencies
uv sync --all-extras

# Run the MCP server
uv run ardour-mcp
```

### Configure Ardour OSC

1. Open Ardour
2. Go to **Edit → Preferences → Control Surfaces**
3. Enable **Open Sound Control (OSC)**
4. Configure:
   - **OSC Server Port**: 3819 (default)
   - **Feedback**: Enable all feedback options
   - Click **OK**

### Using with Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ardour": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ardour-mcp",
        "run",
        "ardour-mcp"
      ]
    }
  }
}
```

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - System design and components
- [Development Guide](docs/DEVELOPMENT.md) - Setup and contribution workflow
- [OSC API Reference](docs/OSC_API.md) - Complete Ardour OSC command reference
- [Roadmap](docs/ROADMAP.md) - Feature timeline and milestones

## 🏗️ Architecture

Ardour MCP uses a three-layer architecture:

```
┌─────────────────┐
│   AI Assistant  │  (Claude, etc.)
└────────┬────────┘
         │ MCP Protocol
┌────────▼────────┐
│   MCP Server    │  (ardour_mcp)
│  ┌──────────┐   │
│  │  Tools   │   │  Transport, Tracks, Mixer, etc.
│  └────┬─────┘   │
│  ┌────▼─────┐   │
│  │  State   │   │  Cached Ardour state
│  └────┬─────┘   │
│  ┌────▼─────┐   │
│  │OSC Bridge│   │  Bidirectional OSC communication
│  └────┬─────┘   │
└───────┼─────────┘
        │ OSC Protocol (UDP)
┌───────▼─────────┐
│     Ardour      │  Digital Audio Workstation
└─────────────────┘
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design.

## 🤝 Contributing

We welcome contributions from developers, musicians, and audio engineers!

- Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- Look for issues labeled [`good first issue`](https://github.com/raibid-labs/ardour-mcp/labels/good%20first%20issue)
- Join discussions about features and design
- Help improve documentation
- Test and report bugs

## 📋 Current Status

**Phase 1 (MVP)** - Foundation

- ✅ Project structure and documentation
- 🚧 OSC communication layer (in progress)
- 🚧 Core MCP tools (in progress)
- 📋 State management (planned)
- 📋 Testing infrastructure (planned)

Target: February 2025

See [ROADMAP.md](docs/ROADMAP.md) for detailed timeline.

## 🎓 Resources

- [Ardour Manual](https://manual.ardour.org/) - Official Ardour documentation
- [Ardour OSC Documentation](https://manual.ardour.org/using-control-surfaces/controlling-ardour-with-osc/) - OSC protocol reference
- [MCP Specification](https://modelcontextprotocol.io/) - Model Context Protocol documentation
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Python implementation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ardour](https://ardour.org/) - Professional open-source DAW
- [Anthropic](https://www.anthropic.com/) - Model Context Protocol
- All contributors and testers

## 📧 Contact

- **GitHub Issues**: [Bug reports and feature requests](https://github.com/raibid-labs/ardour-mcp/issues)
- **Discussions**: [Questions and community chat](https://github.com/raibid-labs/ardour-mcp/discussions)
- **Maintainer**: Raibid Labs

---

**Built with ❤️ for the open-source audio and AI communities**

*First MCP server for professional audio production • Bridging creativity and AI assistance*
