#!/usr/bin/env python3
"""
MIDI to Audio to Ardour Pipeline
=================================

Complete workflow for generating MIDI programmatically, rendering to audio,
and importing into Ardour via ardour-mcp.

This script demonstrates:
1. Programmatic MIDI generation (808 bass pattern, drum beats)
2. MIDI to WAV rendering via FluidSynth
3. Audio import to Ardour via MCP
4. Complete pipeline automation

Requirements:
- FluidSynth (system package): sudo apt-get install fluidsynth
- Soundfont file (SF2): Available at /usr/share/sounds/sf2/ or custom path
- Python packages: midiutil, pretty_midi (installed via: uv pip install midiutil pretty_midi)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Check if midiutil is available
try:
    from midiutil import MIDIFile
except ImportError:
    print("ERROR: midiutil not installed. Run: uv pip install midiutil")
    sys.exit(1)


class MIDIGenerator:
    """Generate MIDI files programmatically for common music production patterns."""

    def __init__(self, output_dir: str = "/tmp/midi_test"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_808_bass_pattern(self, filename: str = "808_bass.mid") -> Path:
        """
        Create an 808-style bass pattern.

        Pattern: Kick on 1 and 3, bass notes following kick rhythm
        Tempo: 120 BPM
        Duration: 4 bars
        """
        midi_file = MIDIFile(1)  # 1 track
        track = 0
        channel = 0
        time = 0  # Start at beat 0
        tempo = 120

        midi_file.addTempo(track, time, tempo)
        midi_file.addTrackName(track, time, "808 Bass")
        midi_file.addProgramChange(track, channel, time, 38)  # Synth Bass 1

        # 808 bass pattern (4 bars = 16 beats)
        # Beat positions and notes (MIDI note numbers)
        pattern = [
            (0.0, 36, 100, 0.5),   # C2 - bar 1 beat 1 (kick)
            (0.5, 36, 80, 0.25),   # C2 - offbeat
            (2.0, 36, 100, 0.5),   # C2 - bar 1 beat 3
            (3.5, 36, 90, 0.25),   # C2 - anticipation

            (4.0, 36, 100, 0.5),   # C2 - bar 2 beat 1
            (5.0, 38, 85, 0.5),    # D2 - variation
            (6.0, 36, 100, 0.5),   # C2 - bar 2 beat 3
            (7.5, 41, 80, 0.25),   # F2 - leading tone

            (8.0, 43, 95, 1.0),    # G2 - bar 3 beat 1 (tension)
            (10.0, 43, 90, 0.5),   # G2 - bar 3 beat 3
            (11.5, 41, 85, 0.25),  # F2 - walkdown

            (12.0, 36, 100, 0.5),  # C2 - bar 4 beat 1 (resolution)
            (13.5, 36, 90, 0.25),  # C2 - anticipation
            (14.0, 36, 100, 0.5),  # C2 - bar 4 beat 3
            (15.5, 36, 85, 0.25),  # C2 - leading to loop
        ]

        for beat, pitch, velocity, duration in pattern:
            midi_file.addNote(track, channel, pitch, beat, duration, velocity)

        output_path = self.output_dir / filename
        with open(output_path, "wb") as f:
            midi_file.writeFile(f)

        print(f"Created 808 bass pattern: {output_path}")
        return output_path

    def create_drum_pattern(self, filename: str = "drum_beat.mid") -> Path:
        """
        Create a standard drum pattern.

        Pattern: Kick, snare, hi-hat groove
        Tempo: 120 BPM
        Duration: 2 bars
        """
        midi_file = MIDIFile(1)
        track = 0
        channel = 9  # MIDI channel 10 (9 in zero-indexed) is drums
        time = 0
        tempo = 120

        midi_file.addTempo(track, time, tempo)
        midi_file.addTrackName(track, time, "Drum Beat")

        # General MIDI Drum Map
        KICK = 36
        SNARE = 38
        CLOSED_HAT = 42
        OPEN_HAT = 46

        # Pattern for 2 bars (8 beats)
        # (beat, instrument, velocity, duration)
        pattern = [
            # Bar 1
            (0.0, KICK, 100, 0.5),
            (0.0, CLOSED_HAT, 80, 0.25),
            (0.5, CLOSED_HAT, 60, 0.25),
            (1.0, SNARE, 95, 0.5),
            (1.0, CLOSED_HAT, 85, 0.25),
            (1.5, CLOSED_HAT, 60, 0.25),
            (2.0, KICK, 100, 0.5),
            (2.0, CLOSED_HAT, 80, 0.25),
            (2.5, CLOSED_HAT, 60, 0.25),
            (3.0, SNARE, 95, 0.5),
            (3.0, OPEN_HAT, 90, 0.5),
            (3.5, KICK, 85, 0.25),

            # Bar 2
            (4.0, KICK, 100, 0.5),
            (4.0, CLOSED_HAT, 80, 0.25),
            (4.5, CLOSED_HAT, 60, 0.25),
            (5.0, SNARE, 95, 0.5),
            (5.0, CLOSED_HAT, 85, 0.25),
            (5.5, CLOSED_HAT, 60, 0.25),
            (6.0, KICK, 100, 0.5),
            (6.0, CLOSED_HAT, 80, 0.25),
            (6.5, KICK, 85, 0.25),
            (7.0, SNARE, 95, 0.5),
            (7.0, OPEN_HAT, 90, 0.5),
            (7.5, CLOSED_HAT, 70, 0.25),
        ]

        for beat, pitch, velocity, duration in pattern:
            midi_file.addNote(track, channel, pitch, beat, duration, velocity)

        output_path = self.output_dir / filename
        with open(output_path, "wb") as f:
            midi_file.writeFile(f)

        print(f"Created drum pattern: {output_path}")
        return output_path

    def create_melodic_sequence(self, filename: str = "melody.mid") -> Path:
        """
        Create a simple melodic sequence.

        Pattern: C major scale melody with rhythm
        Tempo: 120 BPM
        Duration: 4 bars
        """
        midi_file = MIDIFile(1)
        track = 0
        channel = 0
        time = 0
        tempo = 120

        midi_file.addTempo(track, time, tempo)
        midi_file.addTrackName(track, time, "Melody")
        midi_file.addProgramChange(track, channel, time, 0)  # Acoustic Grand Piano

        # Melodic phrase in C major
        # (beat, note, velocity, duration)
        pattern = [
            (0.0, 60, 90, 1.0),    # C4 - whole note feel
            (1.0, 62, 85, 0.5),    # D4
            (1.5, 64, 85, 0.5),    # E4
            (2.0, 65, 90, 1.0),    # F4
            (3.0, 64, 80, 0.5),    # E4
            (3.5, 62, 80, 0.5),    # D4

            (4.0, 67, 95, 2.0),    # G4 - hold
            (6.0, 65, 85, 0.5),    # F4
            (6.5, 64, 85, 0.5),    # E4
            (7.0, 62, 80, 0.5),    # D4
            (7.5, 60, 80, 0.5),    # C4

            (8.0, 64, 90, 1.0),    # E4
            (9.0, 67, 90, 1.0),    # G4
            (10.0, 69, 95, 1.0),   # A4
            (11.0, 67, 85, 1.0),   # G4

            (12.0, 72, 100, 4.0),  # C5 - final note, held
        ]

        for beat, pitch, velocity, duration in pattern:
            midi_file.addNote(track, channel, pitch, beat, duration, velocity)

        output_path = self.output_dir / filename
        with open(output_path, "wb") as f:
            midi_file.writeFile(f)

        print(f"Created melodic sequence: {output_path}")
        return output_path


class FluidSynthRenderer:
    """Render MIDI files to audio using FluidSynth."""

    def __init__(self, soundfont_path: Optional[str] = None):
        """
        Initialize FluidSynth renderer.

        Args:
            soundfont_path: Path to SF2 soundfont file. If None, will search common locations.
        """
        self.soundfont_path = self._find_soundfont(soundfont_path)
        self._check_fluidsynth()

    def _check_fluidsynth(self) -> None:
        """Check if FluidSynth is installed."""
        try:
            result = subprocess.run(
                ["fluidsynth", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"FluidSynth found: {result.stdout.strip()}")
            else:
                raise FileNotFoundError("FluidSynth not working properly")
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print("ERROR: FluidSynth not found or not working.")
            print("\nTo install FluidSynth:")
            print("  Ubuntu/Debian: sudo apt-get install fluidsynth")
            print("  Fedora/RHEL:   sudo dnf install fluidsynth")
            print("  Arch:          sudo pacman -S fluidsynth")
            print("  macOS:         brew install fluid-synth")
            print("\nFluidSynth is required to render MIDI to audio.")
            raise SystemExit(1) from e

    def _find_soundfont(self, custom_path: Optional[str] = None) -> str:
        """Find a soundfont file in common locations."""
        if custom_path and Path(custom_path).exists():
            print(f"Using custom soundfont: {custom_path}")
            return custom_path

        # Common soundfont locations
        common_paths = [
            "/usr/share/sounds/sf2/FluidR3_GM.sf2",
            "/usr/share/sounds/sf2/default.sf2",
            "/usr/share/soundfonts/FluidR3_GM.sf2",
            "/usr/share/soundfonts/default.sf2",
            "/usr/local/share/soundfonts/FluidR3_GM.sf2",
            str(Path.home() / ".soundfonts/FluidR3_GM.sf2"),
        ]

        for path in common_paths:
            if Path(path).exists():
                print(f"Found soundfont: {path}")
                return path

        print("\nWARNING: No soundfont found in common locations.")
        print("Soundfonts checked:")
        for path in common_paths:
            print(f"  - {path}")
        print("\nTo download a free soundfont:")
        print("  1. Download FluidR3_GM.sf2 from: https://github.com/musescore/MuseScore/raw/master/share/sound/FluidR3Mono_GM.sf3")
        print("  2. Or install: sudo apt-get install fluid-soundfont-gm")
        print("  3. Or provide custom path with --soundfont argument")

        # Return a placeholder - will fail at render time if not found
        return "/usr/share/sounds/sf2/FluidR3_GM.sf2"

    def render(self, midi_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Render MIDI file to WAV audio.

        Args:
            midi_path: Path to input MIDI file
            output_path: Path for output WAV file (auto-generated if None)

        Returns:
            Path to rendered WAV file
        """
        if not Path(self.soundfont_path).exists():
            print(f"\nERROR: Soundfont not found at: {self.soundfont_path}")
            print("Please install a soundfont or provide a custom path.")
            raise FileNotFoundError(f"Soundfont not found: {self.soundfont_path}")

        if output_path is None:
            output_path = midi_path.with_suffix(".wav")

        # FluidSynth command to render MIDI to WAV
        # -ni: no interactive mode
        # -g: gain/volume (0.5 = 50% to avoid clipping)
        # -F: output to file
        # -T: audio file type (wav)
        # -r: sample rate (44100 Hz)
        cmd = [
            "fluidsynth",
            "-ni",           # No interactive mode
            "-g", "0.5",     # Gain at 50%
            "-F", str(output_path),  # Output file
            "-T", "wav",     # Output format
            "-r", "44100",   # Sample rate
            self.soundfont_path,  # Soundfont
            str(midi_path),  # Input MIDI file
        ]

        print(f"\nRendering MIDI to audio...")
        print(f"  Input:  {midi_path}")
        print(f"  Output: {output_path}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"  Success! Audio file created ({size_mb:.2f} MB)")
                return output_path
            else:
                print(f"  ERROR: Rendering failed")
                print(f"  Return code: {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
                raise RuntimeError("FluidSynth rendering failed")

        except subprocess.TimeoutExpired:
            print("  ERROR: Rendering timed out (>30 seconds)")
            raise


def demonstrate_pipeline():
    """Demonstrate the complete MIDI → Audio → Ardour pipeline."""

    print("=" * 70)
    print("MIDI to Audio to Ardour Pipeline Demonstration")
    print("=" * 70)

    # Step 1: Generate MIDI files
    print("\nStep 1: Generating MIDI files programmatically...")
    print("-" * 70)
    generator = MIDIGenerator()

    midi_files = [
        generator.create_808_bass_pattern(),
        generator.create_drum_pattern(),
        generator.create_melodic_sequence(),
    ]

    # Step 2: Render MIDI to audio
    print("\n\nStep 2: Rendering MIDI to audio with FluidSynth...")
    print("-" * 70)

    try:
        renderer = FluidSynthRenderer()
        audio_files = []

        for midi_file in midi_files:
            try:
                audio_file = renderer.render(midi_file)
                audio_files.append(audio_file)
            except Exception as e:
                print(f"  Failed to render {midi_file.name}: {e}")
                continue

        # Step 3: Document Ardour import
        print("\n\nStep 3: Import audio to Ardour via ardour-mcp")
        print("-" * 70)
        print("\nAudio files ready for import:")
        for audio_file in audio_files:
            print(f"  - {audio_file}")

        print("\n\nTo import these files into Ardour using ardour-mcp:")
        print("\n1. Start Ardour and create/open a session")
        print("2. Enable OSC control surface in Ardour preferences")
        print("3. In Claude (with ardour-mcp), run commands like:")
        print("\n   'Create a new audio track called Bass and import")
        for audio_file in audio_files:
            name = audio_file.stem.replace('_', ' ').title()
            print(f"    {audio_file}'")

        print("\n   Or use the MCP tools directly to:")
        print("   - Create tracks for each audio file")
        print("   - Import audio regions to tracks")
        print("   - Set up mixing (gain, pan, sends)")
        print("   - Add automation")

        print("\n\nPipeline Summary:")
        print("-" * 70)
        print(f"  MIDI files created: {len(midi_files)}")
        print(f"  Audio files rendered: {len(audio_files)}")
        print(f"  Ready for Ardour import: Yes")

        return audio_files

    except Exception as e:
        print(f"\n\nERROR in rendering pipeline: {e}")
        print("\nPlease ensure FluidSynth and soundfonts are installed:")
        print("  sudo apt-get install fluidsynth fluid-soundfont-gm")
        return []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="MIDI to Audio to Ardour Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate MIDI and render to audio (if FluidSynth available)
  python midi_to_audio_pipeline.py

  # Use custom soundfont
  python midi_to_audio_pipeline.py --soundfont ~/mysounds/piano.sf2

  # Generate MIDI only (no rendering)
  python midi_to_audio_pipeline.py --midi-only
        """
    )

    parser.add_argument(
        "--soundfont",
        help="Path to custom soundfont file (.sf2)",
        default=None
    )

    parser.add_argument(
        "--midi-only",
        action="store_true",
        help="Generate MIDI files only, skip audio rendering"
    )

    parser.add_argument(
        "--output-dir",
        default="/tmp/midi_test",
        help="Output directory for generated files (default: /tmp/midi_test)"
    )

    args = parser.parse_args()

    if args.midi_only:
        print("Generating MIDI files only (audio rendering skipped)...")
        generator = MIDIGenerator(args.output_dir)
        midi_files = [
            generator.create_808_bass_pattern(),
            generator.create_drum_pattern(),
            generator.create_melodic_sequence(),
        ]
        print(f"\nGenerated {len(midi_files)} MIDI files in {args.output_dir}")
    else:
        # Run full demonstration
        demonstrate_pipeline()
