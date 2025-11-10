# Quick Start: MIDI to Audio to Ardour Pipeline

Get started with the complete MIDI generation, audio rendering, and Ardour import pipeline in 5 minutes.

## TL;DR - Fastest Path

```bash
# 1. Generate MIDI (works now, no setup needed)
uv run python scripts/midi_to_audio_pipeline.py --midi-only

# 2. Install FluidSynth for audio rendering
sudo apt-get install fluidsynth fluid-soundfont-gm

# 3. Generate MIDI + render to audio
uv run python scripts/midi_to_audio_pipeline.py

# 4. Start Ardour, enable OSC, import audio
# 5. Use Claude to mix via ardour-mcp
```

## Step-by-Step Guide

### Step 1: Generate MIDI Files (2 minutes)

**No installation needed** - This works right now!

```bash
cd /home/beengud/raibid-labs/ardour-mcp

# Generate three MIDI patterns
uv run python scripts/midi_to_audio_pipeline.py --midi-only
```

**Output**:
```
Created 808 bass pattern: /tmp/midi_test/808_bass.mid
Created drum pattern: /tmp/midi_test/drum_beat.mid
Created melodic sequence: /tmp/midi_test/melody.mid

Generated 3 MIDI files in /tmp/midi_test
```

**What you get**:
- 808 Bass: 4-bar bass line with kick rhythm
- Drum Beat: 2-bar groove with kick, snare, hi-hats
- Melody: 4-bar C major melodic phrase

### Step 2: Install FluidSynth (1 minute)

**Required for audio rendering**:

```bash
sudo apt-get update
sudo apt-get install fluidsynth fluid-soundfont-gm
```

**Verify installation**:
```bash
fluidsynth --version
# Output: FluidSynth runtime version X.X.X

ls /usr/share/sounds/sf2/
# Output: FluidR3_GM.sf2 (or similar)
```

**Skip this step if**:
- You don't have sudo access (use online MIDI renderers instead)
- You only want MIDI files (manual rendering later)

### Step 3: Render MIDI to Audio (1 minute)

```bash
uv run python scripts/midi_to_audio_pipeline.py
```

**Output**:
```
Rendering MIDI to audio...
  Input:  /tmp/midi_test/808_bass.mid
  Output: /tmp/midi_test/808_bass.wav
  Success! Audio file created (1.20 MB)

[Same for drum_beat.wav and melody.wav]

Audio files ready for import:
  - /tmp/midi_test/808_bass.wav
  - /tmp/midi_test/drum_beat.wav
  - /tmp/midi_test/melody.wav
```

**Preview audio**:
```bash
aplay /tmp/midi_test/808_bass.wav  # Linux
afplay /tmp/midi_test/808_bass.wav # macOS
```

### Step 4: Import to Ardour (3 minutes)

#### A. Setup Ardour (one-time)

1. Start Ardour
2. Create or open a session
3. Enable OSC:
   - Edit → Preferences → Control Surfaces
   - Enable "Open Sound Control (OSC)"
   - Set port to 3819
   - Enable all feedback options
   - Click OK

#### B. Create Tracks with Claude

Open Claude (with ardour-mcp configured) and say:

```
Create three stereo audio tracks called:
- 808 Bass
- Drum Beat
- Melody

Set all to 0dB gain and enable input monitoring.
```

**Claude responds**:
```
✓ Created 3 stereo audio tracks
✓ Gain set to 0dB
✓ Input monitoring enabled
Ready to import audio!
```

#### C. Import Audio Files

**In Ardour**:
1. Session → Import
2. Navigate to `/tmp/midi_test/`
3. Select all three .wav files
4. Click "Add files to region list" or "Add as new tracks"
5. Drag files to corresponding tracks

### Step 5: Mix with Claude (2 minutes)

Continue the conversation with Claude:

```
Set up the mix:
- Pan bass to center
- Pan drums 20% left
- Pan melody 20% right
- Create a Mix Bus
- Route all three tracks to the Mix Bus at -6dB
- Check for clipping
```

**Claude responds**:
```
✓ Bass: Pan center (0.0)
✓ Drums: Pan -0.2 (20% left)
✓ Melody: Pan +0.2 (20% right)
✓ Created Mix Bus
✓ Routed all tracks at -6dB
✓ Checked levels:
  - Bass: -8.2dB peak (no clipping)
  - Drums: -6.5dB peak (no clipping)
  - Melody: -9.1dB peak (no clipping)
Ready for final mixing!
```

## Alternative Workflows

### Without FluidSynth (No Sudo Access)

```bash
# 1. Generate MIDI
uv run python scripts/midi_to_audio_pipeline.py --midi-only

# 2. Render online
# Visit: https://solmire.com/
# Upload MIDI files, download WAV

# 3. Continue from Step 4 above
```

### Custom MIDI Patterns

```python
# Create your own pattern
from midiutil import MIDIFile

midi = MIDIFile(1)
midi.addTempo(0, 0, 140)
midi.addNote(0, 0, 60, 0, 1.0, 100)  # C4

with open("/tmp/my_pattern.mid", "wb") as f:
    midi.writeFile(f)
```

### Batch Processing

```bash
# Generate multiple variations
for i in {1..5}; do
    uv run python scripts/midi_to_audio_pipeline.py \
        --output-dir /tmp/batch_$i
done
```

## Common Commands

### Generate MIDI Only
```bash
uv run python scripts/midi_to_audio_pipeline.py --midi-only
```

### Generate with Custom Soundfont
```bash
uv run python scripts/midi_to_audio_pipeline.py \
    --soundfont ~/soundfonts/BetterPiano.sf2
```

### Custom Output Directory
```bash
uv run python scripts/midi_to_audio_pipeline.py \
    --output-dir ~/my_music
```

### Show Import Workflow
```bash
uv run python scripts/ardour_import_example.py
```

### Launch Jupyter Notebook
```bash
uv pip install jupyter  # One-time
uv run jupyter notebook scripts/midi_pipeline_demo.ipynb
```

## Troubleshooting

### "FluidSynth not found"
```bash
sudo apt-get install fluidsynth
```

### "Soundfont not found"
```bash
sudo apt-get install fluid-soundfont-gm
ls /usr/share/sounds/sf2/  # Verify
```

### "Permission denied" on /tmp
```bash
# Use home directory
uv run python scripts/midi_to_audio_pipeline.py \
    --output-dir ~/midi_output
```

### "Audio is clipping"
The script uses `-g 0.5` (50% gain) by default. If still clipping:
```bash
# Edit script or render manually with lower gain
fluidsynth -ni -g 0.3 ...  # 30% gain
```

### "Can't connect to Ardour"
1. Check Ardour OSC is enabled (Edit → Preferences)
2. Check port is 3819
3. Check feedback options are enabled
4. Restart Ardour

## What Next?

### Explore Documentation
- [MIDI_TO_AUDIO_PIPELINE.md](docs/MIDI_TO_AUDIO_PIPELINE.md) - Complete guide
- [scripts/README.md](scripts/README.md) - Script details
- [USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md) - All MCP tools

### Try Advanced Features
```
Claude: "Set up gain automation on the melody track in TOUCH mode"
Claude: "Add a reverb send to all tracks at -12dB"
Claude: "Check LUFS loudness and phase correlation"
Claude: "Create markers at bars 1, 5, 9, and 13"
```

### Customize Patterns
Edit `/home/beengud/raibid-labs/ardour-mcp/scripts/midi_to_audio_pipeline.py`:
- Change tempos (default: 120 BPM)
- Modify note patterns
- Add more instruments
- Create longer sequences

### Integrate with AI
```python
# Generate MIDI with AI
ai_midi = generate_with_ai()

# Render with FluidSynth
renderer.render(ai_midi)

# Import to Ardour via Claude
# "Create track and import /tmp/ai_generated.wav"
```

## Full Workflow Example

```bash
# Complete production pipeline
cd /home/beengud/raibid-labs/ardour-mcp

# 1. Generate and render
uv run python scripts/midi_to_audio_pipeline.py

# 2. Start Ardour (in another terminal)
ardour9

# 3. In Claude Desktop/Code:
"Create 3 stereo tracks: 808 Bass, Drum Beat, Melody"

# 4. In Ardour:
# Session → Import → /tmp/midi_test/*.wav

# 5. In Claude:
"Mix these tracks:
 - Bass: center, -3dB
 - Drums: 10% left, -3dB
 - Melody: 10% right, -3dB
 - Add reverb bus with sends at -12dB
 - Check levels and LUFS
 - Set up markers for intro/verse/chorus"

# 6. Continue mixing with 111 MCP tools
# 7. Export final mix
```

## Resources

### Documentation
- [Main README](README.md) - ardour-mcp overview
- [MIDI Pipeline Guide](docs/MIDI_TO_AUDIO_PIPELINE.md) - Complete reference
- [Installation Checklist](INSTALLATION_CHECKLIST.md) - Setup status
- [Pipeline Summary](MIDI_PIPELINE_SUMMARY.md) - Implementation details

### External Links
- [FluidSynth](https://www.fluidsynth.org/) - MIDI synthesizer
- [Ardour](https://ardour.org/) - Digital Audio Workstation
- [MIDI Specification](https://www.midi.org/specifications) - MIDI standard
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP docs

### Support
- [GitHub Issues](https://github.com/raibid-labs/ardour-mcp/issues)
- [Discussions](https://github.com/raibid-labs/ardour-mcp/discussions)

---

**You're all set!** Start generating MIDI now, install FluidSynth when ready, and enjoy AI-assisted music production with ardour-mcp.

**Total time**: 5 minutes to first mix
**Complexity**: Beginner-friendly
**Power**: Professional DAW control via natural language
