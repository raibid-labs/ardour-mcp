# MIDI MCP Server Setup Summary

Complete installation and configuration summary for MIDI MCP Server integration with Ardour MCP.

## Installation Complete

### What Was Installed

**Date**: 2025-11-10

**Components Installed**:
1. MIDI MCP Server by tubone24
2. Node.js dependencies (midi-writer-js, @modelcontextprotocol/sdk)
3. Claude Code MCP configuration

**Installation Locations**:
```
Repository Clone: /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server
Built Server: /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server/build/index.js
Configuration: ~/.claude.json (user-level MCP config)
MCP Server Name: midi-gen
```

### System Requirements Met

| Requirement | Status | Version |
|-------------|--------|---------|
| Node.js | ✓ Installed | v25.1.0 |
| npm | ✓ Installed | v11.6.2 |
| npx | ✓ Installed | v11.6.2 |
| MIDI MCP Server | ✓ Built | v0.1.0 |
| Claude Code | ✓ Configured | Connected |

## Configuration

### Claude Code MCP Configuration

The MIDI MCP Server has been added to Claude Code as `midi-gen`:

```bash
# Verification command
claude mcp get midi-gen

# Output:
# midi-gen:
#   Scope: User config (available in all your projects)
#   Status: ✓ Connected
#   Type: stdio
#   Command: node
#   Args: /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server/build/index.js
```

### Raw Configuration

Located in `~/.claude.json`:

```json
{
  "mcpServers": {
    "midi-gen": {
      "type": "stdio",
      "command": "node",
      "args": [
        "/home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server/build/index.js"
      ]
    }
  }
}
```

## Available Tools

### MCP Tool: create_midi

**Description**: Generates MIDI files from structured JSON music data

**Parameters**:
- `title` (string, required): Composition title
- `composition` (object, optional): Music data object
- `composition_file` (string, optional): Path to JSON file with composition
- `output_path` (string, required): Where to save MIDI file

**Note**: Either `composition` or `composition_file` must be provided.

## Quick Test

### Test 1: Simple MIDI Generation

```
Ask Claude:
"Create a simple C major scale MIDI file and save it to /tmp/test-scale.mid"

Expected Result:
✓ MIDI file created at /tmp/test-scale.mid
✓ 8 notes (C-D-E-F-G-A-B-C)
✓ 120 BPM, Piano instrument
```

### Test 2: Using Composition File

A test composition file has been created at:
```
/tmp/test-midi-composition.json
```

```
Ask Claude:
"Generate a MIDI file from /tmp/test-midi-composition.json and save to /tmp/test-output.mid"

Expected Result:
✓ MIDI file created from JSON
✓ 4 notes (C-E-G-C chord progression)
✓ 120 BPM, Piano
```

## Integration with Ardour MCP

### Both Servers Configured

You now have **two MCP servers** configured in Claude Code:

1. **ardour**: Control Ardour DAW (111 tools)
2. **midi-gen**: Generate MIDI files (1 tool)

### Verify Both Servers

```bash
# List all MCP servers
claude mcp list

# Should show:
# ardour (✓ Connected)
# midi-gen (✓ Connected)
```

### Example Combined Workflow

```
You: "Create a 4-bar piano melody and import it into Ardour"

Claude:
[Uses midi-gen]
✓ Generated /tmp/piano-melody.mid
  - 16 notes
  - 120 BPM, 4/4 time

[Manual import to Ardour required - future feature]
Import the MIDI file:
1. In Ardour: Session → Import
2. Select /tmp/piano-melody.mid
3. Click Import

[Uses ardour after import]
✓ Track renamed to "Piano Melody"
✓ Session tempo set to 120 BPM
✓ Ready for playback
```

## File Locations

### Server Files
```
/home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server/
├── build/
│   └── index.js          # Compiled server executable
├── src/
│   └── index.ts          # TypeScript source
├── examples/
│   └── cline/            # Example usage
├── docs/                 # Documentation
├── node_modules/         # Dependencies
├── package.json
└── README.md
```

### Documentation Files
```
/home/beengud/raibid-labs/ardour-mcp/docs/integrations/
├── MIDI_MCP_SERVER.md        # Complete integration guide
├── MIDI_ARDOUR_WORKFLOW.md   # Workflow examples
└── SETUP_SUMMARY.md          # This file
```

### Test Files
```
/tmp/
└── test-midi-composition.json  # Test composition
```

## Usage Documentation

Complete usage guides are available:

1. **[MIDI MCP Server Guide](MIDI_MCP_SERVER.md)**
   - Installation details
   - Tool documentation
   - Composition format reference
   - Example usage
   - Troubleshooting

2. **[Complete Workflow Guide](MIDI_ARDOUR_WORKFLOW.md)**
   - End-to-end examples
   - Song production workflow
   - Backing track creation
   - Educational content
   - Rapid prototyping

3. **[Main README](../../README.md)**
   - Updated with MIDI integration section
   - Quick start links

## Next Steps

### 1. Test the Installation

```bash
# Test MIDI generation with simple prompt
# In Claude Code, ask:
"Create a simple C major chord (C-E-G) as whole notes and save to /tmp/c-major.mid"
```

### 2. Explore Examples

Review the workflow examples in the documentation:
- Simple MIDI import
- Complete song production
- Backing track creation

### 3. Create Your First Project

Try a complete workflow:
```
1. Generate MIDI backing track
2. Import to Ardour
3. Record live audio
4. Mix with Ardour MCP tools
```

## Maintenance

### Updating MIDI MCP Server

If updates are needed:

```bash
# Navigate to server directory
cd /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server

# Pull latest changes
git pull origin main

# Reinstall dependencies
npm install

# Rebuild
npm run build

# Restart Claude Code or reload MCP servers
claude mcp reload midi-gen
```

### Rebuilding After Changes

If you modify the source code:

```bash
cd /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server
npm run build
```

## Troubleshooting

### Server Not Connecting

**Symptom**: `claude mcp get midi-gen` shows "Disconnected"

**Solutions**:
1. Check Node.js is installed: `node --version`
2. Verify build exists: `ls -l /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server/build/index.js`
3. Check file permissions: `chmod +x /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server/build/index.js`
4. Reload MCP: `claude mcp reload midi-gen`

### MIDI File Not Generated

**Symptom**: No file created at output path

**Solutions**:
1. Check output directory exists and is writable
2. Use absolute paths (not relative)
3. Verify composition JSON is valid
4. Check error messages from Claude

### Invalid JSON Composition

**Symptom**: "Invalid composition format" error

**Solutions**:
1. Validate JSON syntax with `jq` or online validator
2. Ensure `duration` is a string ("4" not 4)
3. Check all required fields present
4. Use `beat` instead of deprecated `startTime`

## Support Resources

### MIDI MCP Server
- **GitHub**: https://github.com/tubone24/midi-mcp-server
- **Issues**: https://github.com/tubone24/midi-mcp-server/issues
- **Author**: tubone24

### Ardour MCP
- **GitHub**: https://github.com/raibid-labs/ardour-mcp
- **Documentation**: /home/beengud/raibid-labs/ardour-mcp/docs/
- **Issues**: https://github.com/raibid-labs/ardour-mcp/issues

### MIDI Standards
- **General MIDI**: https://www.midi.org/specifications-old/item/gm-level-1-sound-set
- **MIDI Specification**: https://www.midi.org/specifications

## Manual Installation Steps (If Needed)

If you need to install on another system, follow these steps:

### 1. Install Node.js

```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20

# Or download from nodejs.org
```

### 2. Clone MIDI MCP Server

```bash
cd /path/to/ardour-mcp
mkdir -p mcp-servers
cd mcp-servers
git clone https://github.com/tubone24/midi-mcp-server.git
cd midi-mcp-server
```

### 3. Build Server

```bash
npm install
npm run build
```

### 4. Configure Claude Code

```bash
claude mcp add --transport stdio midi-gen --scope user \
  -- node /path/to/ardour-mcp/mcp-servers/midi-mcp-server/build/index.js
```

### 5. Verify

```bash
claude mcp get midi-gen
# Should show: Status: ✓ Connected
```

## Uninstallation

If you need to remove the MIDI MCP Server:

### 1. Remove from Claude Code

```bash
claude mcp remove midi-gen -s user
```

### 2. Remove Server Files

```bash
rm -rf /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server
```

### 3. Remove Documentation (Optional)

```bash
rm /home/beengud/raibid-labs/ardour-mcp/docs/integrations/MIDI_*.md
rm /home/beengud/raibid-labs/ardour-mcp/docs/integrations/SETUP_SUMMARY.md
```

### 4. Revert README Changes (Optional)

Remove the MIDI integration section from the main README.

## Configuration Backup

### Current Claude Code MCP Config

Location: `~/.claude.json`

**Backup your configuration**:
```bash
cp ~/.claude.json ~/.claude.json.backup-$(date +%Y%m%d)
```

**Current configured servers**:
- `midi-gen`: MIDI generation
- (Other MCP servers you may have configured)

## Success Indicators

You'll know the installation is successful when:

1. ✓ `claude mcp get midi-gen` shows "Connected"
2. ✓ You can ask Claude to generate MIDI files
3. ✓ Generated MIDI files can be opened in MIDI players
4. ✓ MIDI files import successfully into Ardour
5. ✓ Both `ardour` and `midi-gen` servers work together

## Additional Notes

### Performance

- MIDI generation: Near-instant (<1 second)
- File sizes: Typically 1-10KB for simple compositions
- No network calls required (runs locally)

### Security

- Server runs locally via stdio transport
- No network access required
- Files written to paths you specify
- Uses standard MIDI file format

### Compatibility

- **Works with**: Claude Code, Claude Desktop, any MCP client
- **MIDI Format**: Standard MIDI File (SMF) Format 1
- **Ardour**: Compatible with Ardour 8.x and 9.x
- **OS**: Linux (tested), macOS and Windows (should work)

---

## Quick Reference Card

### Generate MIDI
```
"Create a [description] MIDI file and save to /tmp/output.mid"
```

### Import to Ardour
```
Manual: Session → Import → Select MIDI file
(Automated import coming in Phase 4)
```

### Check Configuration
```bash
claude mcp list
claude mcp get midi-gen
```

### File Paths
```
Server: /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server
Docs: /home/beengud/raibid-labs/ardour-mcp/docs/integrations/
Config: ~/.claude.json
```

---

**Installation Complete!**

You now have a complete AI-assisted music production workflow with MIDI generation and DAW control.

For detailed usage examples, see [MIDI_ARDOUR_WORKFLOW.md](MIDI_ARDOUR_WORKFLOW.md).
