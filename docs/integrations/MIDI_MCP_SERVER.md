# MIDI MCP Server Integration Guide

[![GitHub](https://img.shields.io/badge/GitHub-tubone24%2Fmidi--mcp--server-blue)](https://github.com/tubone24/midi-mcp-server)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-25.1.0+-green.svg)](https://nodejs.org/)

## Overview

The MIDI MCP Server by [tubone24](https://github.com/tubone24) enables AI models to generate MIDI files from text-based music data through the Model Context Protocol. This integration allows Claude Code to programmatically create musical compositions that can be imported directly into Ardour.

**Perfect for**: Generating backing tracks, creating musical sketches, prototyping arrangements, educational content

## What This Enables

With both Ardour MCP and MIDI MCP Server configured, you can:

1. **Generate MIDI compositions** with natural language
2. **Import generated MIDI** into Ardour sessions
3. **Edit and enhance** MIDI with Ardour's tools
4. **Mix with live recordings** for complete productions
5. **Rapid prototyping** of musical ideas

## Installation Status

| Component | Status |
|-----------|--------|
| **Node.js** | v25.1.0 (Installed) |
| **npm** | v11.6.2 (Installed) |
| **MIDI MCP Server** | Installed at `/home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server` |
| **Claude Code Config** | Configured as `midi-gen` |
| **Connection** | Connected and Ready |

## Installation

### Prerequisites

- **Node.js 20.0.0+** (v25.1.0 installed)
- **npm** or **npx** (v11.6.2 installed)
- **Claude Code** or other MCP-compatible client

### Quick Installation

The MIDI MCP Server has been installed and configured in your environment:

```bash
# Server location
/home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server

# Built executable
/home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server/build/index.js
```

### Configuration

The server has been added to Claude Code as `midi-gen`:

```bash
# Verify installation
claude mcp get midi-gen

# Expected output:
# midi-gen:
#   Scope: User config (available in all your projects)
#   Status: ✓ Connected
#   Type: stdio
#   Command: node
#   Args: /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server/build/index.js
```

### Alternative: NPX Installation

If you prefer to run without installation:

```bash
# Add to Claude Code using npx
claude mcp add --transport stdio midi-gen --scope user -- npx -y midi-mcp-server
```

Note: The GitHub repository version is installed locally for better control and reliability.

## Available Tools

The MIDI MCP Server provides **1 powerful tool**:

### create_midi

Generates MIDI files from structured JSON music data.

**Input Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | The title of the composition |
| `composition` | object | One of* | Music data object with tracks, notes, tempo |
| `composition_file` | string | One of* | Absolute path to JSON file containing composition |
| `output_path` | string | Yes | Absolute path where MIDI file will be saved |

*Either `composition` or `composition_file` must be provided

## Composition Format

### Basic Structure

```json
{
  "bpm": 120,
  "timeSignature": {
    "numerator": 4,
    "denominator": 4
  },
  "tracks": [
    {
      "name": "Piano",
      "instrument": 0,
      "notes": [
        {
          "pitch": 60,
          "beat": 1.0,
          "duration": "4",
          "velocity": 100
        }
      ]
    }
  ]
}
```

### Detailed Parameters

#### Top Level

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `bpm` | number | Yes | Tempo in beats per minute | 120 |
| `timeSignature` | object | No | Time signature (default: 4/4) | `{"numerator": 4, "denominator": 4}` |
| `tracks` | array | Yes | Array of instrument tracks | See below |

#### Track Object

| Field | Type | Required | Description | Range/Values |
|-------|------|----------|-------------|--------------|
| `name` | string | No | Track name | Any string |
| `instrument` | number | No | MIDI program number | 0-127 |
| `notes` | array | Yes | Array of note objects | See below |

#### Note Object

| Field | Type | Required | Description | Range/Values |
|-------|------|----------|-------------|--------------|
| `pitch` | number | Yes | MIDI note number | 0-127 (60 = Middle C) |
| `beat` | number | Yes* | Position in beats (1.0 = first beat) | 1.0, 1.5, 2.0, etc. |
| `startTime` | number | Yes* | Alternative to beat (deprecated) | Time in beats |
| `duration` | string | Yes | Note length | "1", "2", "4", "8", "16", "32", "64" |
| `velocity` | number | No | Note volume (default: 100) | 0-127 |
| `channel` | number | No | MIDI channel (default: track index) | 0-15 |

*Either `beat` or `startTime` must be provided. Use `beat` for new compositions.

### Duration Values

| Value | Musical Note | Beats (4/4) |
|-------|--------------|-------------|
| "1" | Whole note | 4 beats |
| "2" | Half note | 2 beats |
| "4" | Quarter note | 1 beat |
| "8" | Eighth note | 0.5 beats |
| "16" | Sixteenth note | 0.25 beats |
| "32" | Thirty-second note | 0.125 beats |
| "64" | Sixty-fourth note | 0.0625 beats |

### MIDI Instrument Numbers (General MIDI)

**Piano (0-7)**:
- 0: Acoustic Grand Piano
- 1: Bright Acoustic Piano
- 2: Electric Grand Piano
- 3: Honky-tonk Piano
- 4: Electric Piano 1
- 5: Electric Piano 2
- 6: Harpsichord
- 7: Clavinet

**Chromatic Percussion (8-15)**:
- 8: Celesta
- 9: Glockenspiel
- 10: Music Box
- 11: Vibraphone
- 12: Marimba
- 13: Xylophone
- 14: Tubular Bells
- 15: Dulcimer

**Organ (16-23)**, **Guitar (24-31)**, **Bass (32-39)**, **Strings (40-47)**, **Ensemble (48-55)**, **Brass (56-63)**, **Reed (64-71)**, **Pipe (72-79)**, **Synth Lead (80-87)**, **Synth Pad (88-95)**, **Synth Effects (96-103)**, **Ethnic (104-111)**, **Percussive (112-119)**, **Sound Effects (120-127)**

See [MIDI.org](https://www.midi.org/specifications-old/item/gm-level-1-sound-set) for complete list.

## Usage Examples

### Example 1: Simple C Major Scale

```json
{
  "bpm": 120,
  "timeSignature": { "numerator": 4, "denominator": 4 },
  "tracks": [
    {
      "name": "Piano",
      "instrument": 0,
      "notes": [
        { "pitch": 60, "beat": 1.0, "duration": "4", "velocity": 100 },
        { "pitch": 62, "beat": 2.0, "duration": "4", "velocity": 100 },
        { "pitch": 64, "beat": 3.0, "duration": "4", "velocity": 100 },
        { "pitch": 65, "beat": 4.0, "duration": "4", "velocity": 100 },
        { "pitch": 67, "beat": 5.0, "duration": "4", "velocity": 100 },
        { "pitch": 69, "beat": 6.0, "duration": "4", "velocity": 100 },
        { "pitch": 71, "beat": 7.0, "duration": "4", "velocity": 100 },
        { "pitch": 72, "beat": 8.0, "duration": "4", "velocity": 100 }
      ]
    }
  ]
}
```

### Example 2: Multi-Track Arrangement

```json
{
  "bpm": 90,
  "timeSignature": { "numerator": 4, "denominator": 4 },
  "tracks": [
    {
      "name": "Bass",
      "instrument": 33,
      "notes": [
        { "pitch": 36, "beat": 1.0, "duration": "2", "velocity": 110 },
        { "pitch": 36, "beat": 3.0, "duration": "2", "velocity": 110 }
      ]
    },
    {
      "name": "Piano Chords",
      "instrument": 0,
      "notes": [
        { "pitch": 60, "beat": 1.0, "duration": "4", "velocity": 80 },
        { "pitch": 64, "beat": 1.0, "duration": "4", "velocity": 80 },
        { "pitch": 67, "beat": 1.0, "duration": "4", "velocity": 80 }
      ]
    },
    {
      "name": "Melody",
      "instrument": 73,
      "notes": [
        { "pitch": 72, "beat": 1.0, "duration": "8", "velocity": 95 },
        { "pitch": 74, "beat": 1.5, "duration": "8", "velocity": 95 },
        { "pitch": 76, "beat": 2.0, "duration": "4", "velocity": 95 }
      ]
    }
  ]
}
```

### Example 3: Using Composition File (Recommended for Large Files)

**Step 1: Create composition file**
```bash
# Create composition JSON file
cat > /tmp/my-composition.json << 'EOF'
{
  "bpm": 128,
  "timeSignature": { "numerator": 4, "denominator": 4 },
  "tracks": [
    {
      "name": "Synth Lead",
      "instrument": 80,
      "notes": [
        { "pitch": 65, "beat": 1.0, "duration": "4", "velocity": 100 },
        { "pitch": 67, "beat": 2.0, "duration": "4", "velocity": 100 }
      ]
    }
  ]
}
EOF
```

**Step 2: Generate MIDI using file**
```javascript
// Claude will use the create_midi tool with composition_file parameter
{
  "title": "My Electronic Track",
  "composition_file": "/tmp/my-composition.json",
  "output_path": "/tmp/electronic-track.mid"
}
```

## Natural Language Prompts

### Example Prompts That Work

**Basic Generation**:
```
"Create a simple piano melody in C major, 120 BPM, 8 bars"
```

**Multi-track**:
```
"Generate a 4-bar drum pattern with kick, snare, and hi-hat at 100 BPM"
```

**Specific Style**:
```
"Create a jazz piano comp with walking bass line in Bb, medium tempo"
```

**Complex Arrangement**:
```
"Make an 8-bar orchestral arrangement with strings, brass, and timpani
playing a heroic theme in D major, 110 BPM"
```

**With File Reference**:
```
"I have a composition in /tmp/song.json. Generate a MIDI file from it
and save to /tmp/output.mid"
```

## Integration with Ardour MCP

### Workflow: Generate and Import MIDI

**1. Generate MIDI File**
```
You: "Create a 4-bar bass line in E minor, 95 BPM, electric bass,
     and save it to /tmp/bassline.mid"

Claude (using midi-gen):
✓ Generated MIDI file: /tmp/bassline.mid
  - 1 track (Electric Bass)
  - 16 notes
  - 95 BPM, 4/4 time
```

**2. Import into Ardour**
```
You: "Import /tmp/bassline.mid into my Ardour session"

Claude (using ardour):
✓ Imported MIDI file to new track "Electric Bass"
✓ Set session tempo to 95 BPM
✓ Ready for playback
```

**3. Enhance and Mix**
```
You: "Add reverb to the bass track and set volume to -8dB"

Claude (using ardour):
✓ Added reverb plugin to Electric Bass
✓ Set track volume to -8.0dB
```

### Complete Production Example

```
You: "I want to create a complete song arrangement. First, generate a
     4-bar chord progression in C major with piano, bass, and drums at
     110 BPM. Then import it into Ardour and set up for recording vocals."

Claude: I'll help you create this arrangement step by step.

[Uses midi-gen to create backing-track.mid]
✓ Generated MIDI file with:
  - Piano: C-Am-F-G chord progression
  - Bass: Root note pattern
  - Drums: Basic rock beat

[Uses ardour to import and configure]
✓ Imported MIDI to Ardour
✓ Created audio track "Vocals"
✓ Enabled input monitoring on vocals
✓ Set session tempo to 110 BPM
✓ Armed vocal track for recording

Your session is ready! The backing track will play while you record vocals.
```

## Best Practices

### 1. Start Small, Build Up

```
# Instead of generating everything at once:
# Step 1: Create bass and drums
# Step 2: Add chord progression
# Step 3: Add melody
# Step 4: Add counter-melody
```

### 2. Use Composition Files for Large Projects

```
# For compositions with >50 notes, use file-based workflow:
1. Generate JSON in a file
2. Reference file path in create_midi
3. Avoids token limit issues
```

### 3. Use Appropriate Velocities

```json
// Dynamics add realism
{
  "notes": [
    { "pitch": 60, "beat": 1.0, "duration": "4", "velocity": 100 }, // forte
    { "pitch": 62, "beat": 2.0, "duration": "4", "velocity": 80 },  // mezzo-forte
    { "pitch": 64, "beat": 3.0, "duration": "4", "velocity": 60 },  // piano
    { "pitch": 65, "beat": 4.0, "duration": "4", "velocity": 110 }  // fortissimo
  ]
}
```

### 4. Match Ardour Session Settings

```
# Set MIDI tempo to match Ardour session
# Use same time signature
# This ensures perfect synchronization on import
```

### 5. Organize Output Files

```bash
# Create dedicated directory for MIDI generations
mkdir -p ~/ardour-sessions/my-project/midi-generated

# Use descriptive filenames
/midi-generated/drums-verse.mid
/midi-generated/bass-chorus.mid
/midi-generated/strings-intro.mid
```

## Troubleshooting

### Issue: "Invalid composition format"

**Cause**: JSON structure doesn't match expected format

**Solution**:
- Verify all required fields are present
- Check that `duration` is a string ("4" not 4)
- Ensure `beat` values are numbers (1.0 not "1.0")
- Validate JSON syntax

### Issue: Notes not playing at expected times

**Cause**: Confusion between `beat` and `startTime`

**Solution**:
- Use `beat` field (1-indexed: 1.0 = first beat)
- `beat: 1.0` = start of measure
- `beat: 2.5` = halfway between beat 2 and 3

### Issue: Wrong instrument sounds

**Cause**: Incorrect MIDI program number

**Solution**:
- Verify instrument number against General MIDI spec
- Piano = 0, Electric Bass = 33, Strings = 48
- See instrument table above

### Issue: MIDI file won't import to Ardour

**Cause**: File path issues or corrupted MIDI

**Solution**:
- Use absolute paths for `output_path`
- Verify file was created: `ls -lh /path/to/file.mid`
- Check file size (should be >0 bytes)
- Test MIDI file in another player

### Issue: Token limit errors with large compositions

**Cause**: JSON too large to fit in single message

**Solution**:
- Use `composition_file` parameter instead of `composition`
- Build composition incrementally in a file
- Split into multiple smaller MIDI files

## Advanced Techniques

### 1. Humanization

Add slight variations to make MIDI feel more natural:

```json
{
  "notes": [
    // Vary velocity slightly
    { "pitch": 60, "beat": 1.0, "duration": "4", "velocity": 98 },
    { "pitch": 62, "beat": 2.0, "duration": "4", "velocity": 103 },
    { "pitch": 64, "beat": 3.0, "duration": "4", "velocity": 96 },

    // Use swing timing (slightly delayed eighth notes)
    { "pitch": 67, "beat": 1.0, "duration": "8", "velocity": 100 },
    { "pitch": 69, "beat": 1.6, "duration": "8", "velocity": 95 } // Not exactly 1.5
  ]
}
```

### 2. Layering Sounds

Use multiple tracks with same pitches but different instruments:

```json
{
  "tracks": [
    {
      "name": "Strings Section",
      "instrument": 48,
      "notes": [/* harmony notes */]
    },
    {
      "name": "Brass Section",
      "instrument": 56,
      "notes": [/* same harmony notes */]
    }
  ]
}
```

### 3. Arpeggiation

Create flowing patterns from chords:

```json
{
  "notes": [
    // C major chord arpeggiated
    { "pitch": 60, "beat": 1.00, "duration": "8", "velocity": 100 }, // C
    { "pitch": 64, "beat": 1.25, "duration": "8", "velocity": 100 }, // E
    { "pitch": 67, "beat": 1.50, "duration": "8", "velocity": 100 }, // G
    { "pitch": 72, "beat": 1.75, "duration": "8", "velocity": 100 }, // C
    { "pitch": 67, "beat": 2.00, "duration": "8", "velocity": 100 }, // G
    { "pitch": 64, "beat": 2.25, "duration": "8", "velocity": 100 }  // E
  ]
}
```

### 4. Counter-Melody

Create interesting harmonic movement:

```json
{
  "tracks": [
    {
      "name": "Main Melody",
      "instrument": 0,
      "notes": [
        { "pitch": 72, "beat": 1.0, "duration": "2", "velocity": 100 },
        { "pitch": 71, "beat": 3.0, "duration": "2", "velocity": 100 }
      ]
    },
    {
      "name": "Counter Melody",
      "instrument": 73,
      "notes": [
        { "pitch": 60, "beat": 1.0, "duration": "4", "velocity": 80 },
        { "pitch": 62, "beat": 2.0, "duration": "4", "velocity": 80 },
        { "pitch": 64, "beat": 3.0, "duration": "4", "velocity": 80 },
        { "pitch": 65, "beat": 4.0, "duration": "4", "velocity": 80 }
      ]
    }
  ]
}
```

## Musical Theory Tips

### Common Chord Progressions

**I-V-vi-IV (Pop)**:
```
C major: C - G - Am - F
MIDI notes: [60,64,67] - [55,59,62] - [57,60,64] - [53,57,60]
```

**ii-V-I (Jazz)**:
```
C major: Dm7 - G7 - Cmaj7
MIDI notes: [50,53,57,60] - [55,59,62,65] - [60,64,67,71]
```

**I-IV-V (Blues)**:
```
C major: C - F - G
MIDI notes: [60,64,67] - [53,57,60] - [55,59,62]
```

### Note Reference (MIDI Numbers)

| Octave | C | C# | D | D# | E | F | F# | G | G# | A | A# | B |
|--------|---|----|----|----|----|----|----|----|----|----|----|-----|
| 3 | 48 | 49 | 50 | 51 | 52 | 53 | 54 | 55 | 56 | 57 | 58 | 59 |
| 4 | 60 | 61 | 62 | 63 | 64 | 65 | 66 | 67 | 68 | 69 | 70 | 71 |
| 5 | 72 | 73 | 74 | 75 | 76 | 77 | 78 | 79 | 80 | 81 | 82 | 83 |

Note: Middle C = 60

## File Management

### Recommended Directory Structure

```
~/ardour-sessions/
└── my-project/
    ├── midi-generated/          # Generated MIDI files
    │   ├── drums-verse.mid
    │   ├── bass-chorus.mid
    │   └── strings-intro.mid
    ├── midi-compositions/       # JSON composition files
    │   ├── drums-pattern.json
    │   ├── bass-line.json
    │   └── string-arrangement.json
    └── my-project.ardour        # Ardour session file
```

### Cleanup

```bash
# Remove old generated MIDI files
rm ~/ardour-sessions/my-project/midi-generated/*.mid

# Archive old compositions
tar -czf midi-compositions-backup.tar.gz ~/ardour-sessions/my-project/midi-compositions/
```

## Performance Considerations

### Token Limits

- **Small composition** (<50 notes): Use inline `composition` object
- **Medium composition** (50-200 notes): Use `composition_file`
- **Large composition** (>200 notes): Split into multiple MIDI files

### File Size

- Average MIDI note: ~8 bytes
- 100 notes ≈ 1KB MIDI file
- 1000 notes ≈ 10KB MIDI file

### Processing Time

- Generation: Near-instant (<1 second)
- File I/O: <0.1 seconds
- Total typical workflow: <2 seconds

## Resources

### MIDI MCP Server
- **GitHub**: https://github.com/tubone24/midi-mcp-server
- **Author**: tubone24
- **License**: MIT
- **Issues**: https://github.com/tubone24/midi-mcp-server/issues

### MIDI Standards
- **General MIDI**: https://www.midi.org/specifications-old/item/gm-level-1-sound-set
- **MIDI Specification**: https://www.midi.org/specifications
- **MIDI.org**: https://www.midi.org/

### Music Theory
- **Music Theory.net**: https://www.musictheory.net/
- **teoria.com**: https://www.teoria.com/
- **Chord Progressions**: https://www.hooktheory.com/

### Related Tools
- **Ardour MCP**: Control Ardour DAW via MCP
- **ToneJS**: JavaScript MIDI library
- **MIDI.js**: Browser-based MIDI playback

## Uninstallation

If you need to remove the MIDI MCP Server:

```bash
# Remove from Claude Code
claude mcp remove midi-gen -s user

# Remove server files
rm -rf /home/beengud/raibid-labs/ardour-mcp/mcp-servers/midi-mcp-server

# Verify removal
claude mcp list
```

## Support

### Getting Help

1. **Check Examples**: Review usage examples in this document
2. **Check GitHub Issues**: https://github.com/tubone24/midi-mcp-server/issues
3. **Test with Simple Case**: Start with a basic C major scale
4. **Validate JSON**: Use a JSON validator to check composition format

### Reporting Issues

When reporting issues, include:
- Node.js version (`node --version`)
- MIDI MCP Server version
- Full composition JSON (if small) or excerpt
- Error messages (if any)
- Expected vs actual behavior

---

**Integration Complete!**

The MIDI MCP Server is now configured and ready to use with Claude Code. Combined with Ardour MCP, you have a complete AI-assisted music production workflow.
