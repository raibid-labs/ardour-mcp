# MIDI to Audio to Ardour Pipeline

Complete guide for generating MIDI programmatically, rendering to audio, and importing into Ardour using ardour-mcp.

## Overview

This pipeline enables fully automated music production workflows:

```
┌─────────────────┐
│ Python MIDI Gen │  Generate patterns programmatically
│   (midiutil)    │  (808 bass, drums, melodies)
└────────┬────────┘
         │ .mid files
┌────────▼────────┐
│   FluidSynth    │  Render MIDI to audio
│  (soundfonts)   │  using professional soundfonts
└────────┬────────┘
         │ .wav files
┌────────▼────────┐
│     Ardour      │  Import and mix audio
│  (via MCP)      │  using natural language control
└─────────────────┘
```

## Prerequisites

### Required System Packages

```bash
# FluidSynth (MIDI to audio renderer)
sudo apt-get install fluidsynth fluid-soundfont-gm  # Ubuntu/Debian
sudo dnf install fluidsynth fluid-soundfont-gm      # Fedora/RHEL
sudo pacman -S fluidsynth soundfont-fluid           # Arch Linux
brew install fluid-synth                             # macOS
```

### Required Python Packages

Already installed in the ardour-mcp environment:

```bash
# Using uv (recommended)
uv pip install midiutil pretty_midi

# Or using pip in virtual environment
pip install midiutil pretty_midi
```

### Verify Installation

```bash
# Check FluidSynth
fluidsynth --version

# Check soundfonts
ls -l /usr/share/sounds/sf2/

# Check Python packages
uv run python -c "import midiutil; print('midiutil OK')"
```

## Quick Start

### 1. Generate MIDI Files

```bash
# Generate MIDI only (no audio rendering)
uv run python scripts/midi_to_audio_pipeline.py --midi-only

# Output:
# - /tmp/midi_test/808_bass.mid
# - /tmp/midi_test/drum_beat.mid
# - /tmp/midi_test/melody.mid
```

### 2. Render MIDI to Audio (Requires FluidSynth)

```bash
# Full pipeline: Generate MIDI + Render to audio
uv run python scripts/midi_to_audio_pipeline.py

# With custom soundfont
uv run python scripts/midi_to_audio_pipeline.py \
  --soundfont ~/soundfonts/YamahaGrandPiano.sf2

# Output:
# - /tmp/midi_test/808_bass.wav
# - /tmp/midi_test/drum_beat.wav
# - /tmp/midi_test/melody.wav
```

### 3. Import to Ardour via Claude

With ardour-mcp configured in Claude:

```
You: "Create three stereo tracks called '808 Bass', 'Drum Beat', and 'Melody'.
     Set them all to 0dB gain and enable input monitoring."

Claude: ✓ Created 3 stereo audio tracks
        ✓ Gain set to 0dB on all tracks
        ✓ Input monitoring enabled

You: "Now I'll import the audio files manually, then set up mixing:
     - Pan bass center
     - Pan drums 20% left
     - Pan melody 20% right
     - Create a reverb bus and send all three tracks to it at -12dB"

Claude: ✓ Bass: center (0.0)
        ✓ Drums: 20% left (-0.2)
        ✓ Melody: 20% right (+0.2)
        ✓ Created 'Reverb Bus' track
        ✓ Configured sends at -12dB
```

## Usage Examples

### Generate Custom MIDI Patterns

```python
from scripts.midi_to_audio_pipeline import MIDIGenerator

# Initialize generator
generator = MIDIGenerator(output_dir="/tmp/my_music")

# Generate patterns
bass_file = generator.create_808_bass_pattern("my_bass.mid")
drums_file = generator.create_drum_pattern("my_drums.mid")
melody_file = generator.create_melodic_sequence("my_melody.mid")

print(f"Created MIDI files:")
print(f"  - {bass_file}")
print(f"  - {drums_file}")
print(f"  - {melody_file}")
```

### Render MIDI to Audio

```python
from pathlib import Path
from scripts.midi_to_audio_pipeline import FluidSynthRenderer

# Initialize renderer
renderer = FluidSynthRenderer(
    soundfont_path="/usr/share/sounds/sf2/FluidR3_GM.sf2"
)

# Render MIDI files
midi_file = Path("/tmp/midi_test/808_bass.mid")
audio_file = renderer.render(midi_file)

print(f"Rendered: {audio_file}")
# Output: /tmp/midi_test/808_bass.wav
```

### Custom MIDI Pattern

```python
from midiutil import MIDIFile

# Create MIDI file (1 track)
midi = MIDIFile(1)
track = 0
channel = 0
tempo = 140

midi.addTempo(track, 0, tempo)
midi.addTrackName(track, 0, "Custom Bass")
midi.addProgramChange(track, channel, 0, 38)  # Synth Bass

# Add notes (time, pitch, velocity, duration)
notes = [
    (0.0, 36, 100, 0.5),   # C2
    (0.5, 36, 80, 0.25),
    (1.0, 38, 90, 0.5),    # D2
    (2.0, 41, 95, 1.0),    # F2
]

for time, pitch, velocity, duration in notes:
    midi.addNote(track, channel, pitch, time, duration, velocity)

# Write to file
with open("/tmp/custom_bass.mid", "wb") as f:
    midi.writeFile(f)
```

## FluidSynth Rendering Options

### Basic Rendering

```bash
fluidsynth -ni -g 0.5 -F output.wav -T wav -r 44100 \
  /usr/share/sounds/sf2/FluidR3_GM.sf2 input.mid
```

Options:
- `-ni`: No interactive mode (batch processing)
- `-g 0.5`: Gain at 50% (prevents clipping)
- `-F output.wav`: Output file path
- `-T wav`: Output format (wav, aiff, au, raw)
- `-r 44100`: Sample rate (44100, 48000, 96000)

### High-Quality Rendering

```bash
fluidsynth -ni \
  -g 0.4 \                    # Lower gain for headroom
  -F output.wav \
  -T wav \
  -r 48000 \                  # Higher sample rate
  -C 1 \                      # Enable chorus
  -R 1 \                      # Enable reverb
  -z 256 \                    # Buffer size
  /path/to/soundfont.sf2 \
  input.mid
```

### Multiple Soundfonts

```bash
# Layer multiple soundfonts for richer sound
fluidsynth -ni -g 0.5 -F output.wav -T wav -r 44100 \
  piano.sf2 \
  strings.sf2 \
  drums.sf2 \
  input.mid
```

## Soundfonts

### Free Soundfonts

1. **FluidR3_GM** (General MIDI)
   - Included with fluid-soundfont-gm package
   - Location: `/usr/share/sounds/sf2/FluidR3_GM.sf2`
   - Size: ~140 MB
   - Quality: Good for general use

2. **MuseScore Soundfonts**
   - Download: https://musescore.org/en/handbook/3/soundfonts-and-sfz-files
   - MuseScore_General.sf3 (35 MB, compressed)
   - High quality, optimized

3. **TimGM6mb** (Tiny General MIDI)
   - Very small (6 MB)
   - Good for testing
   - Lower quality but fast

### Commercial Soundfonts

For production use, consider commercial soundfonts:
- Soundfont.com collections
- Native Instruments libraries
- Vienna Symphonic Library
- EastWest Quantum Leap

### Soundfont Locations

Common installation paths:
```bash
/usr/share/sounds/sf2/              # System-wide (Linux)
/usr/share/soundfonts/              # Alternative location
/usr/local/share/soundfonts/        # User-installed
~/.soundfonts/                      # User directory
~/Library/Audio/Sounds/Banks/       # macOS
C:\soundfonts\                      # Windows
```

## Integration with Ardour

### Manual Audio Import

After rendering, import audio files in Ardour:

1. **Menu Method**:
   - Session → Import
   - Select audio files
   - Choose "Add files as new tracks" or "Import to region list"

2. **Drag and Drop**:
   - Drag audio files from file browser
   - Drop onto track or editor window

3. **Via ardour-mcp** (Future Feature):
   - Currently, audio import is manual in Ardour
   - Use MCP to create tracks and configure routing
   - Then import audio manually

### Track Setup Workflow

```
1. Generate MIDI → Render audio
   ↓
2. Start Ardour, create/open session
   ↓
3. Use Claude + ardour-mcp to create tracks
   "Create 3 stereo tracks: Bass, Drums, Melody"
   ↓
4. Import audio files manually (drag to tracks)
   ↓
5. Use Claude + ardour-mcp for mixing
   "Set up parallel compression on drums..."
   "Add reverb send to melody at -10dB..."
```

### Example Session Setup

```
You: "Set up a session for these three audio files. Create tracks,
     set initial gains, and route them to a mix bus for mastering."

Claude: ✓ Created tracks: Bass, Drums, Melody
        ✓ Set all to -3dB for headroom
        ✓ Created Mix Bus
        ✓ Routed all tracks to Mix Bus
        ✓ Mix Bus output to Master
        Ready to import audio files!

You: [Import audio files manually]

You: "Check my mix. Show me peak levels, LUFS, and phase correlation."

Claude: Mix Bus: -8.2dB peak, -14.5 LUFS ✓
        Phase: +0.82 (good stereo image) ✓
        No clipping detected ✓
        Ready for mastering!
```

## Advanced Workflows

### AI-Generated MIDI

Combine with AI MIDI generation:

```python
# Generate MIDI with AI (example)
from midi_generator import AIComposer

composer = AIComposer()
midi_data = composer.generate(
    style="808 trap",
    tempo=140,
    bars=16
)

# Save to file
midi_data.write("/tmp/ai_beat.mid")

# Render to audio
renderer = FluidSynthRenderer()
audio_file = renderer.render("/tmp/ai_beat.mid")

# Import to Ardour (via Claude)
# "Import /tmp/ai_beat.wav to a new track called 'AI Beat'"
```

### Batch Processing

Process multiple MIDI files:

```python
from pathlib import Path
from scripts.midi_to_audio_pipeline import FluidSynthRenderer

renderer = FluidSynthRenderer()
midi_dir = Path("/path/to/midi/files")

for midi_file in midi_dir.glob("*.mid"):
    try:
        audio_file = renderer.render(midi_file)
        print(f"✓ {midi_file.name} → {audio_file.name}")
    except Exception as e:
        print(f"✗ {midi_file.name}: {e}")
```

### Automation Example

Complete automated workflow:

```bash
#!/bin/bash
# automated_music_pipeline.sh

# 1. Generate MIDI patterns
echo "Generating MIDI..."
uv run python scripts/midi_to_audio_pipeline.py --midi-only

# 2. Render to audio
echo "Rendering audio..."
for midi in /tmp/midi_test/*.mid; do
    wav="${midi%.mid}.wav"
    fluidsynth -ni -g 0.5 -F "$wav" -T wav -r 44100 \
        /usr/share/sounds/sf2/FluidR3_GM.sf2 "$midi"
    echo "  ✓ $(basename $wav)"
done

# 3. List files for import
echo ""
echo "Audio files ready for Ardour:"
ls -lh /tmp/midi_test/*.wav

echo ""
echo "Next steps:"
echo "1. Start Ardour"
echo "2. Use Claude to create tracks"
echo "3. Import audio files"
echo "4. Use Claude to set up mixing"
```

## Troubleshooting

### FluidSynth Not Found

```bash
# Check if installed
which fluidsynth

# Install if missing
sudo apt-get install fluidsynth  # Ubuntu/Debian
```

### Soundfont Not Found

```bash
# Find installed soundfonts
find /usr -name "*.sf2" 2>/dev/null

# Install default soundfonts
sudo apt-get install fluid-soundfont-gm

# Or download FluidR3_GM manually
wget https://example.com/FluidR3_GM.sf2 -O ~/.soundfonts/FluidR3_GM.sf2
```

### MIDI Files Not Playing

```bash
# Test MIDI file
fluidsynth -a alsa -m alsa_seq /usr/share/sounds/sf2/FluidR3_GM.sf2 test.mid

# Check MIDI file format
file test.mid
# Should show: "Standard MIDI data (format 0 or 1)"
```

### Audio Quality Issues

**Problem**: Rendered audio sounds bad or clipped

**Solutions**:
```bash
# Lower gain to prevent clipping
fluidsynth -ni -g 0.3 ...  # 30% gain instead of 50%

# Use higher quality soundfont
fluidsynth -ni ... ~/soundfonts/BetterPiano.sf2 ...

# Enable effects
fluidsynth -ni -C 1 -R 1 ...  # Chorus + Reverb

# Higher sample rate
fluidsynth -ni ... -r 96000 ...  # 96kHz instead of 44.1kHz
```

### Permission Issues

```bash
# Can't write to output directory
mkdir -p ~/midi_output
chmod 755 ~/midi_output

# Use custom output directory
uv run python scripts/midi_to_audio_pipeline.py \
  --output-dir ~/midi_output
```

## Performance Tips

### Fast Rendering

For quick iteration:
- Use smaller soundfonts (TimGM6mb)
- Lower sample rate (22050 Hz)
- Disable effects (-C 0 -R 0)
- Reduce gain calculation (-g 1.0)

### High Quality Rendering

For final production:
- Use professional soundfonts (200+ MB)
- Higher sample rate (96000 Hz)
- Enable all effects
- Consider 24-bit output (use `-O s24`)

### Batch Processing

```bash
# Parallel rendering with GNU parallel
parallel -j 4 'fluidsynth -ni -g 0.5 -F {.}.wav -T wav \
  /usr/share/sounds/sf2/FluidR3_GM.sf2 {}' ::: /tmp/midi_test/*.mid
```

## Available MCP Tools

After audio import, control Ardour via these ardour-mcp tools:

### Track Management (5 tools)
- `create_audio_track` - Create stereo/mono tracks
- `rename_track` - Rename tracks
- `select_track` - Select track for operations
- `get_track_list` - List all tracks
- `get_track_info` - Get detailed track info

### Mixer Controls (14 tools)
- `set_track_gain` / `set_track_gain_batch` - Volume control
- `set_track_pan` / `set_track_pan_batch` - Pan position
- `set_track_mute` / `set_track_solo` - Mute/solo
- Plus 8 more mixer tools

### Advanced Mixing (15 tools)
- `create_send` - Add send/aux routing
- `set_send_gain` - Control send levels
- `add_plugin_to_track` - Add effects
- Plus 12 more advanced tools

### Automation (13 tools)
- `set_automation_mode` - Set touch/write/play modes
- `clear_automation` - Clear automation data
- `get_automation_state` - Check automation status
- Plus 10 more automation tools

### Metering (12 tools)
- `get_track_peak_level` - Check peak meters
- `get_track_phase_correlation` - Phase analysis
- `get_track_lufs` - Loudness (LUFS) measurement
- `detect_clipping` - Find clipping issues
- Plus 8 more metering tools

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for complete tool reference.

## Example Outputs

### MIDI File Information

```bash
$ file /tmp/midi_test/*.mid
808_bass.mid:  Standard MIDI data (format 1) using 2 tracks at 1/960
drum_beat.mid: Standard MIDI data (format 1) using 2 tracks at 1/960
melody.mid:    Standard MIDI data (format 1) using 2 tracks at 1/960
```

### Audio File Information

```bash
$ file /tmp/midi_test/*.wav
808_bass.wav:  RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, stereo 44100 Hz
drum_beat.wav: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, stereo 44100 Hz
melody.wav:    RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, stereo 44100 Hz

$ ls -lh /tmp/midi_test/*.wav
-rw-rw-r-- 1 user user 1.2M Nov 10 13:45 808_bass.wav
-rw-rw-r-- 1 user user 1.4M Nov 10 13:45 drum_beat.wav
-rw-rw-r-- 1 user user 2.8M Nov 10 13:45 melody.wav
```

## Further Reading

- [FluidSynth Documentation](https://www.fluidsynth.org/)
- [MIDI File Format Specification](https://www.midi.org/specifications)
- [General MIDI Standard](https://www.midi.org/specifications/item/general-midi)
- [Ardour Manual](https://manual.ardour.org/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [ardour-mcp Documentation](../README.md)

## Next Steps

1. **Install FluidSynth**: `sudo apt-get install fluidsynth fluid-soundfont-gm`
2. **Generate MIDI**: `uv run python scripts/midi_to_audio_pipeline.py --midi-only`
3. **Render Audio**: `uv run python scripts/midi_to_audio_pipeline.py`
4. **Import to Ardour**: Use Claude with ardour-mcp for track setup and mixing

Happy music production!
