# Quick Start Guide

Get up and running with Ardour MCP in under 5 minutes!

## Prerequisites

- **Ardour 8.x or 9.x** installed and working
- **Python 3.11+** (Python 3.10 also supported)
- **Claude Desktop** (or any MCP-compatible client)
- **uv** package manager (recommended)

## Step 1: Install uv Package Manager

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

## Step 2: Install Ardour MCP

```bash
# Clone the repository
git clone https://github.com/raibid-labs/ardour-mcp.git
cd ardour-mcp

# Install dependencies (creates virtual environment automatically)
uv sync --all-extras

# Test the installation
uv run ardour-mcp --help
```

## Step 3: Configure Ardour OSC

**This is the most important step!** Ardour MCP communicates with Ardour via OSC (Open Sound Control).

1. **Launch Ardour** and open or create a session
2. Go to **Edit → Preferences** (or **Ardour → Preferences** on macOS)
3. Navigate to **Control Surfaces** in the left panel
4. **Enable "Open Sound Control (OSC)"** checkbox
5. Click **Show Protocol Settings** button
6. Configure the following settings:
   - **OSC Server Port**: `3819` (default)
   - **Feedback**: Enable **all feedback options**
     - Send track/bus information
     - Send plugin information
     - Send metering information
     - Send signal information
   - **Port Mode**: Select **Manual (Specify Below)**
   - **Reply Manual Port**: `8000` (or any available port)
7. Click **OK** to save

**Important**: The feedback options allow ardour-mcp to receive real-time updates from Ardour about track states, meter levels, automation, and more.

## Step 4: Configure Claude Desktop

Add ardour-mcp to your Claude Desktop MCP configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ardour": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/ardour-mcp",
        "run",
        "ardour-mcp"
      ]
    }
  }
}
```

**Replace** `/absolute/path/to/ardour-mcp` with the actual path where you cloned the repository.

Example:
```json
{
  "mcpServers": {
    "ardour": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/yourname/projects/ardour-mcp",
        "run",
        "ardour-mcp"
      ]
    }
  }
}
```

## Step 5: Restart Claude Desktop

Close and reopen Claude Desktop completely to load the new MCP server configuration.

## Step 6: Verify Connection

1. **Make sure Ardour is running** with a session open
2. **Open Claude Desktop**
3. Look for the MCP server indicator (🔌 icon) in the Claude Desktop interface
4. **Test the connection** by asking Claude:

```
"List all tracks in my Ardour session"
```

If everything is configured correctly, Claude will respond with information about your Ardour tracks!

## Troubleshooting

### "Not connected to Ardour" error

- Verify Ardour is running with a session open
- Check that OSC is enabled in Ardour preferences
- Verify the OSC server port is 3819
- Make sure no firewall is blocking UDP port 3819

### MCP server not appearing in Claude Desktop

- Check that the path in `claude_desktop_config.json` is absolute and correct
- Verify uv is installed: `uv --version`
- Check Claude Desktop logs for error messages
- Try restarting Claude Desktop again

### "Command not found: uv"

- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Make sure uv is in your PATH
- Try logging out and back in to refresh your shell environment

### OSC feedback not working

- In Ardour OSC preferences, make sure **all feedback options** are enabled
- Verify feedback is set to send to a specific port
- Check that no other application is using the OSC ports

## Next Steps

Now that you're connected, explore what you can do:

- Read the [Example Conversations](EXAMPLE_CONVERSATIONS.md) for practical workflows
- Check out the [Usage Examples](USAGE_EXAMPLES.md) for specific features
- See [RECORDING_EXAMPLE_USAGE.md](../RECORDING_EXAMPLE_USAGE.md) for recording workflows
- Explore [AUTOMATION_USAGE.md](../AUTOMATION_USAGE.md) for automation control
- Learn about [METERING_USAGE.md](../METERING_USAGE.md) for mixing and mastering

## What's Available?

With **111 MCP tools** across 9 categories, you can:

### 🚀 Transport Control (11 tools)
- Play, stop, pause, record
- Timeline navigation
- Transport state queries

### 🎵 Track Management (5 tools)
- Create audio/MIDI tracks
- Select and rename tracks
- Query track information

### 📝 Session Management (9 tools)
- Session properties
- Tempo and time signature
- Sample rate and duration

### 🎚️ Basic Mixer (14 tools)
- Volume and pan control
- Mute, solo, record-enable
- Batch operations

### 🎛️ Advanced Mixer (15 tools)
- Send/return control
- Plugin management
- Bus operations

### 📍 Navigation (17 tools)
- Markers and loops
- Tempo changes
- Timecode navigation

### 🎙️ Recording (13 tools)
- Recording control
- Punch recording
- Input monitoring

### 🤖 Automation (13 tools)
- Automation modes
- Recording automation
- Automation editing

### 📊 Metering (12 tools)
- Level monitoring
- Phase analysis
- Loudness metering
- Clipping detection

## Getting Help

- **Documentation**: See the [docs/](.) directory
- **Issues**: Report bugs at https://github.com/raibid-labs/ardour-mcp/issues
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

Happy mixing! 🎵
