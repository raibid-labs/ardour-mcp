# Ardour MCP Usage Examples

This document provides practical examples of what you can do with Ardour MCP's **111 tools** organized by category. Use these as a reference for natural language requests to Claude Desktop.

## Table of Contents

- [Recording Workflows](#recording-workflows)
- [Mixing Operations](#mixing-operations)
- [Advanced Mixer](#advanced-mixer)
- [Automation Control](#automation-control)
- [Metering & Analysis](#metering--analysis)
- [Transport & Navigation](#transport--navigation)
- [Track Management](#track-management)
- [Session Information](#session-information)
- [Complex Workflows](#complex-workflows)

---

## 🎙️ Recording Workflows

Control recording operations through natural language.

### Basic Recording

```
"Start recording on tracks 1 and 2"
"Stop recording"
"Toggle record enable"
"Check if I'm currently recording"
"Which tracks are armed for recording?"
```

### Punch Recording

```
"Set up punch recording from bar 5 to bar 9"
"Enable punch in at 30 seconds and punch out at 45 seconds"
"Disable punch recording"
"What are my punch in/out points?"
```

### Track Arming

```
"Arm all tracks with 'Guitar' in the name for recording"
"Arm tracks 1, 3, and 5"
"Disarm all tracks"
"How many tracks are armed?"
"Arm the bass track"
```

### Input Monitoring

```
"Enable input monitoring on track 3"
"Set all tracks to auto monitoring mode"
"Disable input monitoring on the drums"
"What's the monitoring mode on track 5?"
```

### Complete Recording Setup

```
"Set up for recording: arm tracks 2 and 3, enable input monitoring,
set the loop from bar 1 to bar 8, and start recording"

"Create a new audio track called 'Vocal Take 3', arm it, enable input
monitoring, and set up punch recording from bar 16 to bar 24"

"Start recording with automatic punch in/out from the Verse marker
to the Chorus marker"
```

**See also**: [RECORDING_EXAMPLE_USAGE.md](../RECORDING_EXAMPLE_USAGE.md)

---

## 🎚️ Mixing Operations

Control basic mixer functions with natural commands.

### Volume Control

```
"Set track 1 volume to -6dB"
"Bring the vocal track up by 3dB"
"Turn down the drums to -10dB"
"What's the current gain on track 3?"
"Reset all track gains to 0dB"
```

### Panning

```
"Pan track 1 30% to the left"
"Pan the guitar hard right"
"Center the vocals"
"Pan drums to -0.5 (left)"
"What's the pan position on track 5?"
```

### Mute & Solo

```
"Mute track 4"
"Solo tracks 2, 3, and 5 together"
"Unmute all tracks"
"Clear all solos"
"Which tracks are currently muted?"
"Is track 3 soloed?"
```

### Record Enable

```
"Enable recording on the bass track"
"Disable record enable on all tracks"
"Record enable tracks 1 through 4"
```

### Batch Operations

```
"Bring all drum tracks down by 3dB"
"Mute all guitar tracks"
"Reset the gain on all tracks"
"Solo all the vocal tracks and mute everything else"
```

**See also**: [MIXER_EXAMPLE_USAGE.md](../MIXER_EXAMPLE_USAGE.md)

---

## 🎛️ Advanced Mixer

Professional mixing features including sends, plugins, and bus routing.

### Send/Return Control

```
"Send track 1 to the reverb bus at -12dB"
"Create a send from the vocal track to bus 2 at -15dB"
"Disable the send on track 3, send number 1"
"Enable all sends on track 5"
"List all sends on track 3"
"What's the level of send 2 on the guitar track?"
"Set send 1 on track 4 to -18dB"
```

### Plugin Management

```
"Enable plugin bypass on track 2"
"Activate the compressor plugin on the vocal track"
"Deactivate all plugins on track 6"
"List all plugins on track 1"
"How many plugins are on the master bus?"
```

### Bus Operations

```
"Create a drum bus and route tracks 1-8 to it"
"Create a new bus called 'Reverb Return'"
"List all buses in the session"
"Route the guitar tracks to bus 3"
"Show me all the sends on the vocal tracks"
```

### Extended Queries

```
"How many sends does track 5 have?"
"Show me the complete mixer state for track 3"
"What's routed to the reverb bus?"
"List all effects buses in the session"
```

### Workflow Examples

```
"Set up a parallel compression bus: create a bus called 'Parallel Comp',
send all drum tracks to it at -10dB, and keep the original tracks active"

"Create reverb and delay buses, send the vocals to reverb at -12dB
and delay at -18dB"

"Add a drum bus, route all drum tracks to it, and set up a send to
the reverb bus at -15dB"
```

**See also**: [ADVANCED_MIXER_USAGE.md](../ADVANCED_MIXER_USAGE.md)

---

## 🤖 Automation Control

Record and edit automation for professional mixing workflows.

### Automation Modes

```
"Set gain automation to write mode on track 1"
"Enable touch automation for pan on track 3"
"Set track 5 to play mode for all automation"
"Turn off automation on the vocal track"
"Use latch mode for gain on track 2"
"What automation mode is track 4 in?"
```

### Recording Automation

```
"Start recording gain automation on track 2"
"Enable automation write for all parameters on track 1"
"Record automation for the pan on track 3"
"Stop automation recording on track 5"
"Disable automation write mode"
```

### Editing Automation

```
"Clear all automation on track 5"
"Clear automation from bar 10 to bar 20 on track 3"
"Delete the gain automation on the vocal track"
"Copy automation from track 1 to track 2"
"Does track 3 have any automation?"
```

### Playback Control

```
"Enable automation playback on track 1"
"Disable automation playback for pan on track 3"
"Turn on automation playback for all tracks"
"Play back the recorded automation on the vocal"
```

### Complete Automation Workflow

```
"Set track 1 to touch mode for gain, start playing from bar 8,
and I'll ride the fader during the chorus"

"Record volume automation on the vocal track from the Verse marker
to the Chorus marker, then play it back"

"Enable write mode for pan automation on tracks 3 and 4, I want to
automate the guitar stereo width"

"Clear all automation on track 5 between bars 16 and 24, then set
it to touch mode so I can re-record that section"
```

### Query Automation Status

```
"What automation modes are active on track 'Lead Vocals'?"
"List all automated parameters on track 3"
"Show me the automation state for all tracks"
"Which tracks have gain automation?"
```

**See also**: [AUTOMATION_USAGE.md](../AUTOMATION_USAGE.md)

---

## 📊 Metering & Analysis

Professional metering and analysis tools for mixing and mastering.

### Level Metering

```
"Check the current levels on the master bus"
"Show me the peak levels on track 1"
"What's the master output level?"
"Get peak levels for all drum tracks"
"Monitor levels on tracks 1-4 for the next 10 seconds"
"Export metering data for tracks 1-4"
```

### Phase Analysis

```
"Detect any phase issues in my mix"
"Check the phase correlation on track 1"
"Measure phase correlation on the master output"
"Are there any tracks with phase problems?"
"What's the phase correlation between the stereo guitars?"
```

### Loudness Metering

```
"What's the LUFS loudness of the master output?"
"Measure the integrated loudness on track 5"
"Analyze loudness on the master bus"
"What's my loudness range (LRA)?"
"Check if I'm hitting streaming loudness targets (-14 LUFS)"
```

### Clipping Detection

```
"Are any tracks clipping?"
"Check for clipping on the master bus"
"Detect clipping and show me headroom on all tracks"
"Is the master output clipping?"
"How much headroom do I have on the master?"
```

### Complete Analysis

```
"Analyze my mix: check for phase issues, detect any clipping,
measure the master LUFS loudness, and show me peak levels on all tracks"

"Check the master bus: give me peak levels, LUFS loudness,
phase correlation, and clipping status"

"Monitor all vocal tracks (3, 4, 5) for 30 seconds and export
the metering data with phase correlation analysis"

"I'm preparing for streaming upload - check my master LUFS against
-14 LUFS target, verify no clipping, and check loudness range"
```

### Mix Quality Checks

```
"Is my mix ready for mastering? Check levels, phase, and clipping"
"Analyze the master output for broadcast standards"
"Check if any individual tracks are too hot"
"What's my dynamic range across the whole mix?"
```

**See also**: [METERING_USAGE.md](../METERING_USAGE.md)

---

## 🚀 Transport & Navigation

Control playback and navigate your session.

### Basic Transport

```
"Play from the beginning"
"Stop playback"
"Pause"
"Start playing"
"Is Ardour currently playing?"
"Toggle play/pause"
```

### Navigation

```
"Go to marker 'Chorus' and start playing"
"Jump to the beginning"
"Go to the end of the session"
"Fast forward 10 seconds"
"Rewind 5 seconds"
"Go to bar 16"
"Jump to 1 minute 30 seconds"
```

### Markers

```
"Create a marker called 'Bridge' at the current position"
"Add a marker named 'Solo' at bar 24"
"Delete the marker called 'Intro'"
"Go to the 'Verse' marker"
"List all markers in the session"
"What markers exist between bar 8 and bar 16?"
```

### Loop Control

```
"Set the loop from bar 8 to bar 16"
"Enable loop playback"
"Disable the loop"
"What's the current loop range?"
"Loop the section from the Verse to the Chorus marker"
```

### Tempo & Time Signature

```
"Set the tempo to 95 BPM"
"Change time signature to 3/4"
"What's the current tempo?"
"Set tempo to 140 BPM and time signature to 6/8"
```

### Complete Navigation

```
"Go to the Chorus marker, set a loop from there to the Outro marker,
and start playing"

"Create markers at bars 1, 5, 13, 21, and 29 called Intro, Verse,
Chorus, Bridge, and Outro"

"Set the tempo to 128 BPM, go to bar 8, and start playback"
```

**See also**: [NAVIGATION_EXAMPLE_USAGE.md](../NAVIGATION_EXAMPLE_USAGE.md)

---

## 🎵 Track Management

Create and manage tracks in your session.

### Creating Tracks

```
"Create a new audio track called 'Vocals'"
"Create 3 new audio tracks named 'Guitar 1', 'Guitar 2', 'Bass'"
"Create a MIDI track called 'Drums'"
"Add an audio track"
"Create 2 MIDI tracks for piano and strings"
```

### Track Selection

```
"Select track 3"
"Select the vocal track"
"Switch to track 5"
```

### Track Naming

```
"Rename track 5 to 'Lead Vocal'"
"Change the name of track 3 to 'Bass DI'"
"Rename the first track to 'Kick Drum'"
```

### Track Queries

```
"List all tracks in the session"
"How many tracks are there?"
"Show me all track names"
"What type of track is track 5?"
"List all MIDI tracks"
```

### Complete Track Setup

```
"Create 8 audio tracks for a drum recording: Kick, Snare, Hi-Hat,
Tom 1, Tom 2, Overhead L, Overhead R, Room"

"Set up a vocal stack: create 5 audio tracks called 'Lead Vocal',
'Double', 'Harmony 1', 'Harmony 2', 'Backing'"

"Create a complete band setup: drums (stereo), bass, 2 guitars,
keys (MIDI), and lead vocal"
```

---

## 📝 Session Information

Query session properties and configuration.

### Session Properties

```
"What's the session name?"
"What's the sample rate?"
"How long is the session?"
"What's the session path?"
"Tell me about this session"
```

### Session Configuration

```
"What's the current tempo and time signature?"
"How many tracks are in this session?"
"What's the buffer size?"
"Show me complete session info"
```

### Session Status

```
"What's in my current Ardour session?"
"Give me a session overview"
"List all session properties"
"What's the session duration in minutes?"
```

---

## 🔄 Complex Workflows

Combine multiple tools for complete production tasks.

### Complete Recording Session Setup

```
"Set up a recording session:
- Create 4 audio tracks named 'Guitar', 'Bass', 'Vocals', 'Keys'
- Arm the guitar and bass tracks
- Enable input monitoring on all tracks
- Set a loop from bar 1 to bar 8
- Set tempo to 120 BPM
- Create markers for Intro, Verse, Chorus at bars 1, 5, 9
- Start recording"
```

### Professional Mix Setup

```
"Set up my mix:
- Create a reverb bus and delay bus
- Send all vocals (tracks 3, 4, 5) to reverb at -12dB
- Send lead vocal to delay at -18dB
- Pan guitars (tracks 6, 7) hard left and right
- Set drums (tracks 1, 2) to -3dB
- Set all vocals to -6dB
- Create a drum bus and route drum tracks to it"
```

### Automation Session

```
"Set up automation recording:
- Go to bar 8 (Chorus marker)
- Set track 3 (Lead Vocal) to touch mode for gain
- Enable automation playback on all tracks
- Start loop playback from bar 8 to bar 16
- I'll ride the vocal fader during the chorus"
```

### Mix Analysis Workflow

```
"Complete mix analysis:
- Check master peak levels and LUFS loudness
- Detect any clipping on all tracks
- Find phase issues in the stereo tracks
- Measure loudness range
- Check if we're hitting -14 LUFS for streaming
- Export full metering data"
```

### Session Organization

```
"Organize my session:
- Rename tracks 1-4 to 'Kick', 'Snare', 'Hi-Hat', 'Toms'
- Create markers for all song sections at bars 1, 9, 17, 25, 33
- Set tempo to 95 BPM
- Create a master bus and route all tracks to it
- Set up reverb and delay sends for vocals and guitars"
```

---

## Natural Language Tips

### You Can Say It However You Want

Ardour MCP understands natural language, so you can phrase requests in many ways:

**Volume Control - All These Work:**
- "Turn down track 3"
- "Lower the volume on track 3"
- "Set track 3 to -6dB"
- "Reduce track 3 gain by 3dB"
- "Make track 3 quieter"
- "Decrease the bass level"

**Recording - All These Work:**
- "Start recording"
- "Hit record"
- "Begin recording on armed tracks"
- "Start capturing audio"
- "Record now"

**Navigation - All These Work:**
- "Go to the chorus"
- "Jump to the Chorus marker"
- "Take me to bar 16"
- "Skip to the bridge section"

### Use Track Names or Numbers

Both work equally well:
- "Mute track 3" or "Mute the bass track"
- "Solo track 5" or "Solo the lead vocal"
- "Pan the guitar left" or "Pan track 6 left"

### Combine Actions Naturally

- "Create a vocal track, arm it, and enable monitoring"
- "Go to bar 8 and start recording"
- "Mute the drums and solo the bass"
- "Set up reverb on the vocals at -12dB"

### Ask Questions

- "What's playing?"
- "Which tracks are muted?"
- "Am I recording?"
- "What's my tempo?"
- "How many tracks do I have?"

### Iterate and Correct

- "Actually, make that -8dB instead"
- "No, the other guitar track"
- "That's too much, bring it down to -15dB"
- "Undo that and try -10dB"

---

## What Makes This Powerful?

### No Learning Curve
You don't need to memorize 111 tool names or parameters. Just describe what you want in plain English.

### Contextual Understanding
Claude understands context:
- "the vocal track" (figures out which track based on name)
- "all drum tracks" (finds tracks with "drum" in the name)
- "from the Verse to the Chorus" (uses marker positions)

### Complex Workflows Made Simple
Instead of clicking through menus:
```
"Set up parallel compression: create a bus, send all drums at -10dB,
add a compressor plugin, and blend it with the original drums"
```

### Real-Time Adaptation
The conversation adapts to your session:
- Knows your track names
- Understands your markers
- Tracks your automation status
- Monitors your levels

---

## Next Steps

- Try these examples in your own sessions
- Read the detailed feature guides:
  - [Recording Workflows](../RECORDING_EXAMPLE_USAGE.md)
  - [Automation Control](../AUTOMATION_USAGE.md)
  - [Metering & Analysis](../METERING_USAGE.md)
  - [Advanced Mixer](../ADVANCED_MIXER_USAGE.md)
- See [Example Conversations](EXAMPLE_CONVERSATIONS.md) for complete dialogue examples
- Check the [Quick Start Guide](QUICK_START.md) for setup

Happy producing! 🎵
