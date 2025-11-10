# Installation Checklist - MIDI to Audio to Ardour Pipeline

This document lists what has been installed and what needs manual installation for the complete MIDI to Audio to Ardour pipeline.

## Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Python 3.14 | Installed | Already available |
| uv package manager | Installed | Already available |
| midiutil library | Installed | Successfully installed via uv |
| pretty_midi library | Installed | Successfully installed via uv |
| FluidSynth | **NOT INSTALLED** | Requires sudo - see below |
| Soundfonts | **NOT INSTALLED** | Requires sudo - see below |
| ardour-mcp | Installed | Already configured |

## What's Working Now

### MIDI Generation (Fully Working)
- Generate MIDI files programmatically
- Create 808 bass patterns
- Create drum beats
- Create melodic sequences
- All working without any dependencies

**Test it**:
```bash
uv run python /home/beengud/raibid-labs/ardour-mcp/scripts/midi_to_audio_pipeline.py --midi-only
```

**Output**: Creates MIDI files in `/tmp/midi_test/`
```
/tmp/midi_test/808_bass.mid
/tmp/midi_test/drum_beat.mid
/tmp/midi_test/melody.mid
```

### Documentation (Complete)
All documentation and example code is ready:
- `/home/beengud/raibid-labs/ardour-mcp/scripts/midi_to_audio_pipeline.py`
- `/home/beengud/raibid-labs/ardour-mcp/scripts/ardour_import_example.py`
- `/home/beengud/raibid-labs/ardour-mcp/scripts/midi_pipeline_demo.ipynb`
- `/home/beengud/raibid-labs/ardour-mcp/docs/MIDI_TO_AUDIO_PIPELINE.md`
- `/home/beengud/raibid-labs/ardour-mcp/scripts/README.md`

## What Needs Manual Installation

### FluidSynth (MIDI to Audio Renderer)

**Required for**: Rendering MIDI files to WAV audio

**Installation command**:
```bash
sudo apt-get update
sudo apt-get install fluidsynth fluid-soundfont-gm
```

**Verification**:
```bash
# Check if installed
which fluidsynth

# Check version
fluidsynth --version

# Test basic functionality
fluidsynth --help
```

**Package details**:
- `fluidsynth`: The MIDI synthesizer (audio renderer)
- `fluid-soundfont-gm`: General MIDI soundfont (instruments/sounds)

**Soundfont location after installation**:
- `/usr/share/sounds/sf2/FluidR3_GM.sf2` (default)
- `/usr/share/sounds/sf2/default.sf2` (symlink)

### Alternative: FluidSynth on Other Systems

**Fedora/RHEL**:
```bash
sudo dnf install fluidsynth fluid-soundfont-gm
```

**Arch Linux**:
```bash
sudo pacman -S fluidsynth soundfont-fluid
```

**macOS**:
```bash
brew install fluid-synth
```

## Complete Installation Steps

Run these commands in order:

```bash
# 1. Install FluidSynth and soundfonts (requires sudo)
sudo apt-get update
sudo apt-get install -y fluidsynth fluid-soundfont-gm

# 2. Verify installation
fluidsynth --version
ls -l /usr/share/sounds/sf2/

# 3. Test the complete pipeline
cd /home/beengud/raibid-labs/ardour-mcp
uv run python scripts/midi_to_audio_pipeline.py

# 4. Check output
ls -lh /tmp/midi_test/
# Should show both .mid and .wav files
```

## Post-Installation Testing

### Test 1: MIDI Generation Only
```bash
uv run python scripts/midi_to_audio_pipeline.py --midi-only
```

**Expected output**:
```
Generating MIDI files only (audio rendering skipped)...
Created 808 bass pattern: /tmp/midi_test/808_bass.mid
Created drum pattern: /tmp/midi_test/drum_beat.mid
Created melodic sequence: /tmp/midi_test/melody.mid

Generated 3 MIDI files in /tmp/midi_test
```

**Status**: This works NOW (no sudo needed)

### Test 2: Complete Pipeline (Requires FluidSynth)
```bash
uv run python scripts/midi_to_audio_pipeline.py
```

**Expected output** (after FluidSynth installation):
```
======================================================================
MIDI to Audio to Ardour Pipeline Demonstration
======================================================================

Step 1: Generating MIDI files programmatically...
----------------------------------------------------------------------
Created 808 bass pattern: /tmp/midi_test/808_bass.mid
Created drum pattern: /tmp/midi_test/drum_beat.mid
Created melodic sequence: /tmp/midi_test/melody.mid


Step 2: Rendering MIDI to audio with FluidSynth...
----------------------------------------------------------------------
FluidSynth found: FluidSynth runtime version X.X.X

Rendering MIDI to audio...
  Input:  /tmp/midi_test/808_bass.mid
  Output: /tmp/midi_test/808_bass.wav
  Success! Audio file created (1.20 MB)

Rendering MIDI to audio...
  Input:  /tmp/midi_test/drum_beat.mid
  Output: /tmp/midi_test/drum_beat.wav
  Success! Audio file created (1.40 MB)

Rendering MIDI to audio...
  Input:  /tmp/midi_test/melody.mid
  Output: /tmp/midi_test/melody.wav
  Success! Audio file created (2.80 MB)


Step 3: Import audio to Ardour via ardour-mcp
----------------------------------------------------------------------

Audio files ready for import:
  - /tmp/midi_test/808_bass.wav
  - /tmp/midi_test/drum_beat.wav
  - /tmp/midi_test/melody.wav
```

**Status**: Will work after running sudo apt-get install commands above

### Test 3: Manual MIDI Rendering
```bash
# After installing FluidSynth, test it directly:
fluidsynth -ni -g 0.5 \
  -F /tmp/test_render.wav \
  -T wav \
  -r 44100 \
  /usr/share/sounds/sf2/FluidR3_GM.sf2 \
  /tmp/midi_test/808_bass.mid

# Check output
ls -lh /tmp/test_render.wav
file /tmp/test_render.wav
```

### Test 4: Ardour Import Workflow
```bash
# Show complete workflow documentation
uv run python scripts/ardour_import_example.py
```

**Status**: This works NOW (documentation/examples only)

## Current Workaround (Without FluidSynth)

If you cannot install FluidSynth right now, you can still:

1. **Generate MIDI files**:
   ```bash
   uv run python scripts/midi_to_audio_pipeline.py --midi-only
   ```

2. **Use external tools to render MIDI**:
   - Online MIDI renderers (e.g., solmire.com, onlineconverter.com)
   - Other DAWs (import MIDI, export WAV)
   - Hardware synthesizers

3. **Import rendered audio to Ardour**:
   - Use ardour-mcp to create tracks
   - Import audio files manually
   - Use ardour-mcp for mixing

## Dependencies Summary

### Already Installed (No Action Needed)
- Python 3.14
- uv package manager
- ardour-mcp and all its dependencies
- midiutil (Python MIDI generation library)
- pretty_midi (Python MIDI utilities)
- mido (MIDI I/O library)
- numpy (scientific computing)

### Need Manual Installation (Requires sudo)
- **fluidsynth** - MIDI to audio renderer
- **fluid-soundfont-gm** - General MIDI instruments

### Optional (Enhance functionality)
- **timidity++** - Alternative MIDI renderer
- **lilypond** - Music notation from MIDI
- **sox** - Audio processing utilities
- **jupyter** - For running notebooks

## Alternative MIDI Renderers

If FluidSynth doesn't work for you, alternatives include:

### 1. TiMidity++
```bash
sudo apt-get install timidity timidity-interfaces-extra

# Render MIDI
timidity -Ow -o output.wav input.mid
```

### 2. Online Services
- https://solmire.com/ (MIDI to MP3/WAV)
- https://www.onlineconverter.com/midi-to-wav
- https://audio.online-convert.com/convert-to-wav

### 3. Other DAWs
- Import MIDI into Ardour itself
- Use virtual instruments in Ardour
- Export audio after playing back

## Next Steps

1. **Install FluidSynth** (run the sudo commands above)
2. **Test the pipeline**:
   ```bash
   uv run python scripts/midi_to_audio_pipeline.py
   ```
3. **Start using it**:
   - Generate MIDI programmatically
   - Render to audio
   - Import to Ardour
   - Mix with Claude + ardour-mcp

## Support

If you encounter issues:

1. **Check FluidSynth installation**:
   ```bash
   dpkg -l | grep fluidsynth
   apt-cache policy fluidsynth
   ```

2. **Check soundfont installation**:
   ```bash
   dpkg -L fluid-soundfont-gm | grep sf2
   find /usr -name "*.sf2" 2>/dev/null
   ```

3. **Test components individually**:
   ```bash
   # Test MIDI generation
   uv run python -c "from midiutil import MIDIFile; print('MIDI OK')"

   # Test FluidSynth
   fluidsynth --version

   # Test rendering
   fluidsynth --help
   ```

4. **Check logs**:
   ```bash
   # Run pipeline with verbose output
   uv run python scripts/midi_to_audio_pipeline.py 2>&1 | tee pipeline.log
   ```

## Files Created

All files created by this setup:

### Scripts
- `/home/beengud/raibid-labs/ardour-mcp/scripts/midi_to_audio_pipeline.py` - Main pipeline
- `/home/beengud/raibid-labs/ardour-mcp/scripts/ardour_import_example.py` - Import examples
- `/home/beengud/raibid-labs/ardour-mcp/scripts/midi_pipeline_demo.ipynb` - Jupyter notebook
- `/home/beengud/raibid-labs/ardour-mcp/scripts/README.md` - Scripts documentation

### Documentation
- `/home/beengud/raibid-labs/ardour-mcp/docs/MIDI_TO_AUDIO_PIPELINE.md` - Complete guide
- `/home/beengud/raibid-labs/ardour-mcp/INSTALLATION_CHECKLIST.md` - This file

### Generated Files (temporary)
- `/tmp/midi_test/808_bass.mid` - Generated MIDI
- `/tmp/midi_test/drum_beat.mid` - Generated MIDI
- `/tmp/midi_test/melody.mid` - Generated MIDI
- `/tmp/midi_test/*.wav` - Rendered audio (after FluidSynth install)

## Quick Reference

### Generate MIDI Only
```bash
uv run python scripts/midi_to_audio_pipeline.py --midi-only
```

### Complete Pipeline (with FluidSynth)
```bash
uv run python scripts/midi_to_audio_pipeline.py
```

### Custom Soundfont
```bash
uv run python scripts/midi_to_audio_pipeline.py \
  --soundfont ~/my-soundfonts/piano.sf2
```

### Show Import Workflow
```bash
uv run python scripts/ardour_import_example.py
```

### Launch Jupyter Notebook
```bash
uv pip install jupyter
uv run jupyter notebook scripts/midi_pipeline_demo.ipynb
```

---

**Last Updated**: November 10, 2025
**ardour-mcp Version**: 0.3.0
**Environment**: Python 3.14, uv package manager
