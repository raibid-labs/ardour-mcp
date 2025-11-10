# MIDI MCP + Ardour MCP Workflow Guide

Complete workflows combining MIDI generation with Ardour DAW control for AI-assisted music production.

## Overview

This guide demonstrates real-world workflows using both MCP servers together:

- **MIDI MCP Server** (`midi-gen`): Generate MIDI compositions
- **Ardour MCP** (`ardour`): Control Ardour DAW

## Table of Contents

1. [Quick Start Workflow](#quick-start-workflow)
2. [Complete Song Production](#complete-song-production)
3. [Backing Track Creation](#backing-track-creation)
4. [Sound Design Templates](#sound-design-templates)
5. [Educational Content](#educational-content)
6. [Rapid Prototyping](#rapid-prototyping)

---

## Quick Start Workflow

### Simple MIDI Import Test

**Goal**: Verify both servers work together

```
You: "Create a simple C major arpeggio MIDI file and import it into Ardour"

Claude:
Step 1: Generating MIDI file...
[Uses midi-gen]
✓ Created /tmp/c-major-arpeggio.mid
  - 1 track (Piano)
  - 8 notes (C-E-G-C pattern)
  - 120 BPM

Step 2: Importing to Ardour...
[Uses ardour]
✓ Imported MIDI to track "Piano"
✓ Session tempo set to 120 BPM
✓ Ready for playback
```

**Verify**:
- MIDI file created in `/tmp/`
- Track visible in Ardour
- Playback works

---

## Complete Song Production

### Workflow: From Idea to Mix

**Scenario**: Create a complete pop song with AI-generated backing track and live vocals

#### Step 1: Generate Song Structure

```
You: "I want to create a pop song. Generate a 16-bar backing track with:
     - Drums (kick, snare, hi-hat pattern)
     - Bass line in E minor
     - Chord progression: Em - C - G - D
     - 95 BPM, 4/4 time
     Save each part as a separate MIDI file"

Claude:
Creating your pop song backing track...

[Uses midi-gen for drums]
✓ /tmp/pop-drums.mid
  - Kick: Quarter notes on 1 and 3
  - Snare: Quarter notes on 2 and 4
  - Hi-hat: Eighth note pattern

[Uses midi-gen for bass]
✓ /tmp/pop-bass.mid
  - Root notes: E-C-G-D progression
  - Octave: 2 (low bass)
  - Rhythm: Half notes with passing tones

[Uses midi-gen for chords]
✓ /tmp/pop-chords.mid
  - Piano voicings
  - Inversions for smooth voice leading
  - Sustained whole notes

All files ready at 95 BPM, 4/4 time
```

#### Step 2: Import and Configure Session

```
You: "Import all three MIDI files into a new Ardour session called 'My Pop Song'"

Claude:
[Uses ardour session tools]
✓ Session 'My Pop Song' ready (or using current session)

[Uses ardour import MIDI - Note: Not yet implemented, manual import needed]
Manual step required:
1. In Ardour: Session → Import → Import Audio/MIDI
2. Select all three .mid files
3. Click OK

Alternative: Drag files from file manager to Ardour

I'll wait for import confirmation...

You: "Files imported, I have three MIDI tracks now"

Claude:
[Uses ardour track management]
✓ Renaming tracks...
  - Track 1 → "Drums"
  - Track 2 → "Bass"
  - Track 3 → "Piano Chords"

✓ Setting session tempo to 95 BPM
✓ Time signature confirmed: 4/4
```

#### Step 3: Add Vocal Recording Track

```
You: "Add a vocal track and set it up for recording with input monitoring"

Claude:
[Uses ardour track creation]
✓ Created audio track "Vocals"

[Uses ardour recording setup]
✓ Enabled input monitoring on "Vocals"
✓ Track armed for recording

[Uses ardour mixer]
✓ Set vocal track gain to 0dB (unity)
✓ Pan: Center

Your session is ready to record vocals!
The backing track will play while you record.
```

#### Step 4: Initial Mix Setup

```
You: "Set up a basic mix:
     - Drums at -3dB
     - Bass at -6dB
     - Chords at -12dB
     - Leave vocals at 0dB
     Also pan the chords slightly left (20%)"

Claude:
[Uses ardour mixer tools]
✓ Drums: -3.0dB, center
✓ Bass: -6.0dB, center
✓ Piano Chords: -12.0dB, 20% left
✓ Vocals: 0.0dB, center

Basic mix balance applied!
```

#### Step 5: Add Effects

```
You: "Add reverb to the vocals with a send at -10dB"

Claude:
[Uses ardour advanced mixer]
✓ Created aux bus "Reverb"
✓ Added send from Vocals to Reverb at -10.0dB
✓ Reverb bus ready (add reverb plugin manually)

Recommendation: Add your preferred reverb plugin to the "Reverb" bus
```

#### Step 6: Record and Mix

```
You: "Start recording"

Claude:
[Uses ardour transport]
✓ Recording started
  - Armed tracks: Vocals
  - Backing tracks will play

Record your performance, then say "stop recording" when done.

You: "Stop recording"

Claude:
[Uses ardour transport]
✓ Recording stopped
✓ New region created on Vocals track

You: "Check the vocal recording for clipping"

Claude:
[Uses ardour metering]
✓ Vocals track metering:
  - Peak level: -4.2dB
  - No clipping detected
  - Dynamic range: Good
  - Phase correlation: Mono (as expected)

Your vocal take looks clean!
```

#### Step 7: Final Mix and Export

```
You: "Check the master output levels and set up for export"

Claude:
[Uses ardour metering]
Master Output Analysis:
✓ Peak level: -2.1dB
✓ LUFS (integrated): -14.2 LUFS
✓ Dynamic range: 8.5dB
✓ No clipping
✓ Phase correlation: +0.82 (good stereo image)

Mix is broadcast-ready at -14 LUFS!

To export:
1. Session → Export → Export to Audio File
2. Format: WAV or FLAC recommended
3. Click Export
```

**Result**: Complete song from AI-generated backing track to mixed vocal recording!

---

## Backing Track Creation

### Jazz Practice Track

**Scenario**: Create a jazz backing track for practice

```
You: "Create a jazz backing track in Bb with a ii-V-I progression.
     Include walking bass, piano comping, and brush pattern drums.
     Medium swing tempo, 32 bars"

Claude:
Creating your jazz backing track...

[Uses midi-gen for bass]
✓ /tmp/jazz-bass-walking.mid
  - Walking quarter notes
  - Chord tones and approach notes
  - Progression: Cm7 - F7 - Bbmaj7 - Bbmaj7

[Uses midi-gen for piano]
✓ /tmp/jazz-piano-comp.mid
  - Chord voicings (3rd and 7th emphasis)
  - Syncopated rhythm
  - Voice leading between chords

[Uses midi-gen for drums]
✓ /tmp/jazz-drums-swing.mid
  - Ride cymbal pattern (swing)
  - Light kick on 1 and 3
  - Snare on 2 and 4 (brushes)

All files: 120 BPM (medium swing), 4/4, 32 bars

You: "Import these into Ardour and set up a count-in"

Claude:
[After manual MIDI import]

[Uses ardour session tools]
✓ Set tempo to 120 BPM
✓ Enabled click/metronome

[Uses ardour transport]
✓ Count-in: 2 bars enabled

Ready to practice! Press space to start playback with count-in.
```

---

## Sound Design Templates

### Synth Pad Template

**Scenario**: Create a template for ambient synth pads

```
You: "Create a MIDI template with sustained notes for a pad sound.
     Use different layers at different octaves. Key: A minor, atmospheric"

Claude:
[Uses midi-gen]
✓ /tmp/pad-template.mid
  - Layer 1 (Low): Octave 2, whole notes
  - Layer 2 (Mid): Octave 3, longer sustains
  - Layer 3 (High): Octave 4, textural notes
  - Progression: Am - F - C - G
  - All notes 4 bars duration each

You: "Import this and set up three synth tracks for the layers"

Claude:
[After manual MIDI import and track separation]

[Uses ardour track management]
✓ Created tracks:
  - "Pad Low" (Layer 1)
  - "Pad Mid" (Layer 2)
  - "Pad High" (Layer 3)

[Uses ardour mixer]
✓ Pad Low: -6dB, center
✓ Pad Mid: -8dB, center
✓ Pad High: -12dB, center

Add your synth plugins to each track for layered sound design!
```

---

## Educational Content

### Music Theory Demonstration

**Scenario**: Generate examples for teaching chord inversions

```
You: "Create three MIDI files showing C major triad in:
     1. Root position
     2. First inversion
     3. Second inversion
     Each as whole notes, 60 BPM"

Claude:
[Uses midi-gen for each inversion]

✓ /tmp/c-major-root.mid
  Notes: C4 - E4 - G4 (60-64-67)

✓ /tmp/c-major-first.mid
  Notes: E4 - G4 - C5 (64-67-72)

✓ /tmp/c-major-second.mid
  Notes: G4 - C5 - E5 (67-72-76)

You: "Import these into three tracks and play them in sequence"

Claude:
[After manual MIDI import]

[Uses ardour track management]
✓ Tracks named: "Root Position", "First Inversion", "Second Inversion"

[Uses ardour navigation]
✓ Created markers:
  - "Root Position" at bar 1
  - "First Inversion" at bar 3
  - "Second Inversion" at bar 5

✓ Set tempo to 60 BPM

Use markers to jump between examples during your lesson!
```

---

## Rapid Prototyping

### Quick Idea Capture

**Scenario**: Quickly test a musical idea

```
You: "I have a melody idea. Create a simple MIDI with these notes:
     D - F# - A - G - F# - E - D
     Quarter notes, 100 BPM, piano sound"

Claude:
[Uses midi-gen]
✓ /tmp/melody-idea.mid
  - Notes: D4(62) - F#4(66) - A4(69) - G4(67) - F#4(66) - E4(64) - D4(62)
  - Rhythm: Quarter notes
  - Tempo: 100 BPM
  - Instrument: Acoustic Piano

You: "Import it and add a bass line underneath - roots of D and A"

Claude:
[After manual MIDI import of melody]

[Uses midi-gen for bass]
✓ /tmp/bass-line.mid
  - D2 (bars 1-2), A2 (bars 3-4)
  - Half notes
  - Electric Bass

[After manual import]

[Uses ardour mixer]
✓ Melody: 0dB, center
✓ Bass: -6dB, center

Your idea is ready to hear!
```

---

## Advanced Workflows

### Multi-Genre Template

**Scenario**: Create a template session with various genre starting points

```
You: "Create MIDI templates for:
     - Rock: 4/4 rock beat, power chords
     - EDM: 4/4 four-on-floor kick pattern
     - Jazz: 4/4 swing pattern with walking bass
     - Waltz: 3/4 time signature
     Each 8 bars, 120 BPM"

Claude:
[Uses midi-gen for each genre]

Rock Template:
✓ /tmp/rock-drums.mid - Standard rock beat
✓ /tmp/rock-guitar.mid - Power chord progression (E5-A5-D5)

EDM Template:
✓ /tmp/edm-kick.mid - Four-on-floor pattern
✓ /tmp/edm-bass.mid - Synth bass line

Jazz Template:
✓ /tmp/jazz-drums.mid - Swing ride pattern
✓ /tmp/jazz-bass.mid - Walking bass in Bb

Waltz Template:
✓ /tmp/waltz-drums.mid - 3/4 pattern
✓ /tmp/waltz-bass.mid - Oom-pah bass

Note: Waltz is 3/4, others are 4/4, all 120 BPM

You: "Create four Ardour sessions, one for each genre"

Claude:
This requires creating new sessions manually:

1. Create session "Rock Template"
2. Import rock-drums.mid and rock-guitar.mid
3. Save template

Repeat for EDM, Jazz, and Waltz

Alternative: I can help configure a single session with all templates
on different tracks if you prefer.
```

---

## Tips and Best Practices

### 1. File Organization

```bash
# Create organized directory structure
mkdir -p ~/music-projects/
mkdir -p ~/music-projects/midi-generated
mkdir -p ~/music-projects/compositions
mkdir -p ~/music-projects/ardour-sessions

# Use descriptive naming
/midi-generated/2025-01-10-pop-drums.mid
/midi-generated/2025-01-10-pop-bass.mid
```

### 2. Iterative Development

```
Instead of: "Create a complete 5-minute song"

Do this:
1. "Create 8-bar drum pattern"
2. "Add bass line to match drums"
3. "Create chord progression"
4. "Add melody"
5. "Extend to 16 bars"
6. "Add variations"
```

### 3. Use Tempo Matching

```
Always specify same BPM in MIDI generation and Ardour session
This ensures perfect sync when importing
```

### 4. Layering Strategy

```
Generate separate MIDI files for:
- Different instruments
- Different sections (verse, chorus, bridge)
- Different takes/variations

This gives maximum flexibility in Ardour
```

### 5. Version Control

```
Save multiple versions during experimentation:
/tmp/bass-v1.mid
/tmp/bass-v2-higher.mid
/tmp/bass-v3-syncopated.mid

Import all and mute/unmute to compare
```

---

## Current Limitations and Workarounds

### MIDI Import (Not Yet Implemented)

**Current**: Manual import required in Ardour
**Workaround**:
1. Generate MIDI with `midi-gen`
2. In Ardour: Session → Import → Select MIDI files
3. Confirm import
4. Continue with Ardour MCP tools

**Future**: Direct MIDI import tool coming in Phase 4

### Region Editing (Not Yet Implemented)

**Current**: Cannot move/edit MIDI regions via MCP
**Workaround**: Use Ardour GUI for region manipulation

**Future**: Region tools coming in Phase 4

### Plugin Parameter Control (Not Yet Implemented)

**Current**: Cannot automate plugin parameters via MCP
**Workaround**: Use Ardour GUI for plugin automation

**Future**: Plugin automation coming in Phase 4

---

## Troubleshooting

### MIDI File Not Generating

**Check**:
```bash
# Verify midi-gen is connected
claude mcp get midi-gen

# Test with simple composition
# Ask Claude to create a basic C major scale
```

### MIDI Import Issues

**Check**:
```bash
# Verify file exists
ls -lh /tmp/*.mid

# Check file size (should be > 0)
# Check MIDI is valid (open in another MIDI player)
```

### Tempo Mismatch After Import

**Solution**:
```
Ask Claude: "Set Ardour session tempo to [BPM]"
```

### Tracks Not Playing

**Check**:
```
Ask Claude:
- "Are any tracks muted?"
- "Show me the mixer levels"
- "Is the session at bar 1?"
```

---

## Next Steps

### Phase 4 Enhancements (Coming Q1 2025)

When implemented, you'll be able to:

1. **Direct MIDI Import**:
   ```
   "Generate drums.mid and import it directly to a new track"
   ```

2. **Region Manipulation**:
   ```
   "Move the bass region to start at bar 5"
   "Copy the drum pattern to bars 9-16"
   ```

3. **Plugin Automation**:
   ```
   "Automate the reverb wet/dry mix from 0% to 50% over 8 bars"
   ```

### Provide Feedback

Help shape future development:
- Report issues: https://github.com/raibid-labs/ardour-mcp/issues
- Request features: https://github.com/raibid-labs/ardour-mcp/discussions
- Share workflows: Document what works for you!

---

## Resources

### Documentation
- [MIDI MCP Server Guide](MIDI_MCP_SERVER.md)
- [Ardour MCP Usage Examples](../USAGE_EXAMPLES.md)
- [Ardour MCP Recording Guide](../guides/RECORDING_EXAMPLE_USAGE.md)

### External Resources
- [Ardour Manual](https://manual.ardour.org/)
- [MIDI Specification](https://www.midi.org/)
- [General MIDI Instrument List](https://www.midi.org/specifications-old/item/gm-level-1-sound-set)

---

**Happy Music Making!**

You now have a complete AI-assisted music production workflow combining MIDI generation and DAW control.
