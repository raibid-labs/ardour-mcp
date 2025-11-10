# Ardour MCP Scripts

Utility scripts for MIDI generation, audio rendering, and Ardour integration.

## Available Scripts

### 1. `midi_to_audio_pipeline.py`

Complete pipeline for MIDI generation and audio rendering.

**Features**:
- Generate MIDI programmatically (808 bass, drums, melodies)
- Render MIDI to audio using FluidSynth
- Prepare audio for Ardour import

**Usage**:

```bash
# Generate MIDI files only
uv run python scripts/midi_to_audio_pipeline.py --midi-only

# Generate MIDI and render to audio (requires FluidSynth)
uv run python scripts/midi_to_audio_pipeline.py

# Use custom soundfont
uv run python scripts/midi_to_audio_pipeline.py \
  --soundfont ~/soundfonts/piano.sf2

# Custom output directory
uv run python scripts/midi_to_audio_pipeline.py \
  --output-dir ~/my_music
```

**Output**:
- MIDI files: `/tmp/midi_test/*.mid`
- Audio files: `/tmp/midi_test/*.wav` (if FluidSynth available)

**MIDI Patterns Generated**:
1. **808 Bass Pattern**: 4-bar bass line with kick rhythm
2. **Drum Beat**: 2-bar drum groove (kick, snare, hi-hat)
3. **Melodic Sequence**: 4-bar melody in C major

### 2. `ardour_import_example.py`

Documentation and examples for importing audio to Ardour via MCP.

**Features**:
- MCP workflow examples
- Claude prompt templates
- Direct MCP protocol examples

**Usage**:

```bash
# Show complete import workflow
uv run python scripts/ardour_import_example.py
```

**Output**: Displays step-by-step instructions for:
- Creating tracks via MCP
- Importing audio manually
- Setting up mixing via Claude
- Using MCP tools directly

### 3. `midi_pipeline_demo.ipynb`

Interactive Jupyter notebook demonstrating the complete pipeline.

**Features**:
- Step-by-step MIDI generation
- Audio rendering with FluidSynth
- Audio preview in notebook
- Ardour import instructions
- MCP command examples

**Usage**:

```bash
# Install Jupyter (if not already)
uv pip install jupyter

# Launch notebook
uv run jupyter notebook scripts/midi_pipeline_demo.ipynb
```

## Quick Start

### Prerequisites

**Python packages** (install once):
```bash
uv pip install midiutil pretty_midi
```

**System packages** (for audio rendering):
```bash
# Ubuntu/Debian
sudo apt-get install fluidsynth fluid-soundfont-gm

# Fedora/RHEL
sudo dnf install fluidsynth fluid-soundfont-gm

# Arch Linux
sudo pacman -S fluidsynth soundfont-fluid

# macOS
brew install fluid-synth
```

### Generate and Render

```bash
# 1. Generate MIDI + render audio
uv run python scripts/midi_to_audio_pipeline.py

# 2. Check output
ls -lh /tmp/midi_test/
# Output:
#   808_bass.mid   (208 bytes)
#   808_bass.wav   (1.2 MB)
#   drum_beat.mid  (279 bytes)
#   drum_beat.wav  (1.4 MB)
#   melody.mid     (202 bytes)
#   melody.wav     (2.8 MB)

# 3. Preview audio
aplay /tmp/midi_test/808_bass.wav  # Linux
afplay /tmp/midi_test/808_bass.wav # macOS
```

### Import to Ardour

```bash
# 1. Start Ardour and enable OSC (see README.md)

# 2. Use Claude to create tracks:
# "Create 3 stereo tracks: 808 Bass, Drum Beat, Melody"

# 3. Import audio manually:
# Session → Import → Select /tmp/midi_test/*.wav

# 4. Use Claude for mixing:
# "Pan bass center, drums left, melody right"
# "Add reverb send to all tracks at -12dB"
# "Check for clipping and show peak levels"
```

## Example Workflows

### Workflow 1: Quick Beat Creation

```bash
# Generate MIDI
uv run python scripts/midi_to_audio_pipeline.py --midi-only

# Manual rendering with custom settings
fluidsynth -ni -g 0.6 -C 1 -R 1 \
  -F /tmp/midi_test/808_bass.wav -T wav -r 48000 \
  /usr/share/sounds/sf2/FluidR3_GM.sf2 \
  /tmp/midi_test/808_bass.mid

# Import to Ardour and mix with Claude
```

### Workflow 2: Batch Processing

```python
# custom_midi_batch.py
from pathlib import Path
from midi_to_audio_pipeline import MIDIGenerator, FluidSynthRenderer

# Generate multiple variations
generator = MIDIGenerator("/tmp/beats")
renderer = FluidSynthRenderer()

for i in range(5):
    # Generate MIDI
    midi_file = generator.create_808_bass_pattern(f"bass_v{i}.mid")

    # Render to audio
    audio_file = renderer.render(midi_file)

    print(f"Created: {audio_file}")
```

### Workflow 3: AI Integration

```python
# ai_midi_generator.py
from midi_to_audio_pipeline import FluidSynthRenderer
from midiutil import MIDIFile

# Generate MIDI with AI (example)
def generate_ai_beat(style="trap", tempo=140):
    midi = MIDIFile(1)
    # ... AI generation logic ...
    return midi

# Render AI-generated MIDI
ai_midi = generate_ai_beat()
with open("/tmp/ai_beat.mid", "wb") as f:
    ai_midi.writeFile(f)

renderer = FluidSynthRenderer()
audio = renderer.render("/tmp/ai_beat.mid")

# Import to Ardour via Claude
print(f"Ready for import: {audio}")
```

## MIDI Pattern Details

### 808 Bass Pattern

**Structure**:
- Tempo: 120 BPM
- Duration: 4 bars (16 beats)
- Root: C2 (MIDI note 36)
- Pattern: Kick-driven bass with variations

**Key Features**:
- Bar 1: Root notes on downbeats
- Bar 2: Variation with D2 and F2
- Bar 3: Tension with G2
- Bar 4: Resolution back to C2

**MIDI Notes Used**:
- C2 (36): Root bass/kick
- D2 (38): Minor variation
- F2 (41): Leading tone
- G2 (43): Tension/turnaround

### Drum Beat Pattern

**Structure**:
- Tempo: 120 BPM
- Duration: 2 bars (8 beats)
- General MIDI drum map

**Instruments**:
- Kick (36): On downbeats
- Snare (38): On beats 2 and 4
- Closed Hi-Hat (42): 8th note pattern
- Open Hi-Hat (46): Accents on beat 4

**Pattern**:
```
Bar 1: K-H-S-H-K-H-S-H
Bar 2: K-H-S-H-K+K-S-H
(K=Kick, S=Snare, H=Hi-Hat, +=extra note)
```

### Melodic Sequence

**Structure**:
- Tempo: 120 BPM
- Duration: 4 bars (16 beats)
- Key: C major
- Range: C4 to C5

**Phrase Structure**:
- Bar 1-2: Ascending C major scale
- Bar 3: Development with G4 and A4
- Bar 4: Resolution to C5 (octave)

**MIDI Notes Used**:
- C4, D4, E4, F4, G4, A4, C5
- Velocities: 80-100 (medium to strong)

## Customization

### Create Custom MIDI Patterns

```python
from midiutil import MIDIFile

# Create custom pattern
midi = MIDIFile(1)
track = 0
channel = 0

midi.addTempo(track, 0, 140)  # 140 BPM
midi.addTrackName(track, 0, "My Pattern")

# Add notes (time, pitch, velocity, duration)
notes = [
    (0.0, 60, 100, 1.0),  # C4 at beat 0
    (1.0, 64, 90, 1.0),   # E4 at beat 1
    (2.0, 67, 95, 2.0),   # G4 at beat 2, held
]

for time, pitch, velocity, duration in notes:
    midi.addNote(track, channel, pitch, time, duration, velocity)

# Save
with open("my_pattern.mid", "wb") as f:
    midi.writeFile(f)
```

### Custom Rendering Settings

```python
from midi_to_audio_pipeline import FluidSynthRenderer
import subprocess

# Manual FluidSynth rendering with custom settings
subprocess.run([
    "fluidsynth",
    "-ni",                    # No interactive
    "-g", "0.8",              # Louder gain
    "-C", "1",                # Enable chorus
    "-R", "1",                # Enable reverb
    "-F", "output.wav",       # Output file
    "-T", "wav",              # Format
    "-r", "96000",            # High sample rate
    "/path/to/soundfont.sf2",
    "input.mid"
])
```

## Troubleshooting

### FluidSynth Not Found

```bash
# Install FluidSynth
sudo apt-get install fluidsynth

# Verify installation
which fluidsynth
fluidsynth --version
```

### Soundfont Not Found

```bash
# Install default soundfont
sudo apt-get install fluid-soundfont-gm

# Check installation
ls -l /usr/share/sounds/sf2/

# Use custom soundfont
uv run python scripts/midi_to_audio_pipeline.py \
  --soundfont ~/Downloads/MySoundfont.sf2
```

### Audio Quality Issues

**Clipping**:
```bash
# Lower gain
fluidsynth -ni -g 0.3 ...
```

**Low Quality**:
```bash
# Use better soundfont + higher sample rate
fluidsynth -ni -r 96000 \
  -C 1 -R 1 \
  /path/to/better_soundfont.sf2 \
  input.mid
```

### Permission Errors

```bash
# Use home directory
mkdir -p ~/midi_output
uv run python scripts/midi_to_audio_pipeline.py \
  --output-dir ~/midi_output
```

### Import Errors

```bash
# Ensure packages are installed in venv
uv pip install midiutil pretty_midi

# Verify installation
uv run python -c "import midiutil; print('OK')"
```

## Advanced Usage

### Parallel Rendering

```bash
# Render multiple MIDI files in parallel
find /tmp/midi_test -name "*.mid" | \
  parallel -j 4 'fluidsynth -ni -g 0.5 \
    -F {.}.wav -T wav \
    /usr/share/sounds/sf2/FluidR3_GM.sf2 {}'
```

### Automation Script

```bash
#!/bin/bash
# automated_music_production.sh

set -e

# 1. Generate MIDI
echo "Generating MIDI..."
uv run python scripts/midi_to_audio_pipeline.py --midi-only

# 2. Render audio
echo "Rendering audio..."
for midi in /tmp/midi_test/*.mid; do
    wav="${midi%.mid}.wav"
    fluidsynth -ni -g 0.5 \
      -F "$wav" -T wav -r 44100 \
      /usr/share/sounds/sf2/FluidR3_GM.sf2 "$midi"
done

# 3. Show results
echo ""
echo "Production complete:"
ls -lh /tmp/midi_test/*.wav

echo ""
echo "Next: Import to Ardour using ardour-mcp"
```

### Integration with Other Tools

```bash
# Convert MIDI to Lilypond notation
midi2ly /tmp/midi_test/melody.mid -o melody.ly

# Analyze MIDI file
midicsv /tmp/midi_test/808_bass.mid > bass_analysis.csv

# Combine audio files
sox -m /tmp/midi_test/*.wav /tmp/final_mix.wav
```

## Documentation

- [MIDI to Audio Pipeline Guide](../docs/MIDI_TO_AUDIO_PIPELINE.md) - Complete pipeline documentation
- [Ardour MCP README](../README.md) - Main project documentation
- [Usage Examples](../docs/USAGE_EXAMPLES.md) - MCP tool reference

## Resources

- [FluidSynth Manual](https://www.fluidsynth.org/)
- [MIDI File Format](https://www.midi.org/specifications)
- [General MIDI Spec](https://www.midi.org/specifications/item/general-midi)
- [midiutil Documentation](https://midiutil.readthedocs.io/)
- [pretty_midi Documentation](https://craffel.github.io/pretty-midi/)

## License

MIT License - Same as ardour-mcp parent project
