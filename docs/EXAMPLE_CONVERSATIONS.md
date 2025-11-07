# Example Conversations with Claude Desktop

This guide shows real-world conversations you can have with Claude Desktop to control Ardour through natural language. These examples demonstrate how to combine multiple tools for complete workflows.

## Table of Contents

- [Getting Started](#getting-started)
- [Recording Session Setup](#recording-session-setup)
- [Mixing Workflow](#mixing-workflow)
- [Automation Recording](#automation-recording)
- [Mix Analysis and Metering](#mix-analysis-and-metering)
- [Complete Production Workflow](#complete-production-workflow)
- [Troubleshooting and Queries](#troubleshooting-and-queries)

---

## Getting Started

### Simple Session Inquiry

**You**: "What's in my current Ardour session?"

**Claude**: "Let me check your Ardour session..."
- Session name: "My Song Project"
- Sample rate: 48000 Hz
- Duration: 3 minutes 45 seconds
- Tempo: 120 BPM
- 8 tracks total
  - Track 1: "Drums" (audio)
  - Track 2: "Bass" (audio)
  - Track 3: "Guitar L" (audio)
  - Track 4: "Guitar R" (audio)
  - Track 5: "Keys" (MIDI)
  - Track 6: "Lead Vocal" (audio)
  - Track 7: "Backing Vocals" (audio)
  - Track 8: "Master" (bus)

### Quick Transport Control

**You**: "Play from the beginning"

**Claude**: "Starting playback from the beginning of the session..."
✓ Transport positioned at start
✓ Playback started

**You**: "Stop and go to bar 8"

**Claude**: "Stopping playback and jumping to bar 8..."
✓ Transport stopped
✓ Position: Bar 8, Beat 1

---

## Recording Session Setup

### Creating a Multi-Track Recording Setup

**You**: "I want to record a band. Set up 4 audio tracks called 'Kick', 'Snare', 'Guitar', and 'Vocals'. Arm the kick and snare for recording and enable input monitoring on all of them."

**Claude**: "I'll set up your recording session..."

✓ Created audio track 'Kick' (track 9)
✓ Created audio track 'Snare' (track 10)
✓ Created audio track 'Guitar' (track 11)
✓ Created audio track 'Vocals' (track 12)
✓ Armed tracks 9 and 10 for recording
✓ Enabled input monitoring on tracks 9, 10, 11, 12

Your session is ready to record! Tracks 9 (Kick) and 10 (Snare) are armed and all four tracks are in input monitoring mode so you can hear the incoming signal.

**You**: "Actually, arm all four tracks and set up a click from bar 1 to bar 16"

**Claude**: "Arming all recording tracks and setting up the loop..."

✓ Armed track 11 (Guitar)
✓ Armed track 12 (Vocals)
✓ Set loop region: Bar 1 to Bar 16
✓ Loop enabled

All 4 tracks are now armed. The click will play from bar 1 to bar 16.

**You**: "Start recording!"

**Claude**: "Starting recording now..."

✓ Recording started with 4 armed tracks
✓ Transport playing
✓ Tracks recording: Kick, Snare, Guitar, Vocals

Recording in progress!

---

## Mixing Workflow

### Basic Mix Setup

**You**: "Let's start mixing. Set the drums (tracks 1 and 2) to -3dB, pan the guitars hard left and right, and bring the vocals up to -6dB"

**Claude**: "Adjusting your mix..."

✓ Track 1 (Drums): Gain set to -3.0 dB
✓ Track 2 (Drums): Gain set to -3.0 dB
✓ Track 3 (Guitar L): Panned 100% left (-1.0)
✓ Track 4 (Guitar R): Panned 100% right (+1.0)
✓ Track 6 (Lead Vocal): Gain set to -6.0 dB

Your basic mix is set up!

### Advanced Mixing with Sends

**You**: "Create a reverb bus and send the vocals and guitars to it at -12dB. Also add a delay bus and send just the lead vocal at -18dB"

**Claude**: "Setting up your effects buses and sends..."

✓ Created bus 'Reverb Bus' (bus 1)
✓ Sent track 6 (Lead Vocal) → Reverb Bus at -12.0 dB
✓ Sent track 3 (Guitar L) → Reverb Bus at -12.0 dB
✓ Sent track 4 (Guitar R) → Reverb Bus at -12.0 dB

✓ Created bus 'Delay Bus' (bus 2)
✓ Sent track 6 (Lead Vocal) → Delay Bus at -18.0 dB

Your effects routing is complete! You now have:
- Vocals and both guitars going to the reverb bus
- Lead vocal also going to the delay bus for more space

**You**: "What sends are on the lead vocal track?"

**Claude**: "Checking sends for track 6 (Lead Vocal)..."

Track 6 has 2 sends:
- Send 1 → Reverb Bus: -12.0 dB (enabled)
- Send 2 → Delay Bus: -18.0 dB (enabled)

---

## Automation Recording

### Setting Up Automation

**You**: "I want to automate the vocal volume during the chorus. Set track 6 to write mode for gain automation"

**Claude**: "Setting up gain automation for the lead vocal..."

✓ Track 6 (Lead Vocal): Gain automation mode set to WRITE
✓ All parameter controls will now write automation data

Ready to record automation! Start playback and move the gain fader - all movements will be recorded.

**You**: "Actually, I just want to ride the fader on the chorus, not the whole song. Use touch mode instead"

**Claude**: "Switching to touch mode for more controlled automation..."

✓ Track 6 (Lead Vocal): Gain automation mode set to TOUCH

Perfect! In touch mode, automation will only be written when you're actively touching/moving the fader. When you release it, playback of existing automation resumes.

### Automation Workflow

**You**: "Start playing from bar 16, I'll ride the vocal fader through the chorus"

**Claude**: "Starting playback from bar 16..."

✓ Transport positioned at bar 16
✓ Playback started
✓ Track 6 in TOUCH mode - ready to record gain automation

*(You move the fader in Ardour during playback)*

**You**: "Stop. How does it sound? Play it back with the automation."

**Claude**: "Switching to playback mode and playing from bar 16..."

✓ Track 6: Gain automation mode set to PLAY
✓ Transport positioned at bar 16
✓ Playback started

Your automation is now playing back. The vocal fader will follow your recorded movements.

**You**: "The automation is a bit much in the second half. Clear the automation from bar 24 to bar 32"

**Claude**: "Clearing gain automation on track 6 from bar 24 to bar 32..."

✓ Automation cleared for track 6 (Lead Vocal)
✓ Parameter: gain
✓ Range: Bar 24 to Bar 32

The automation in that section has been removed. You can re-record it if needed.

---

## Mix Analysis and Metering

### Checking Mix Levels

**You**: "How are my levels looking? Check for any clipping or phase issues"

**Claude**: "Analyzing your mix..."

**Level Analysis:**
✓ Master output: -8.2 dB peak, -14.5 LUFS
✓ Headroom: 8.2 dB (healthy)
✓ No clipping detected

**Phase Correlation:**
✓ Master: +0.85 (good stereo image)
✓ Track 3 (Guitar L): +0.92 (mono-ish, expected)
✓ Track 4 (Guitar R): +0.91 (mono-ish, expected)
✓ Track 6 (Lead Vocal): +0.98 (centered)

**Potential Issues:**
⚠ Track 1 (Drums): Phase correlation -0.15 (possible phase issue)

Your mix is in good shape overall! The drums show a slight phase issue which you might want to check. Master levels are healthy with good headroom.

### Detailed Metering

**You**: "Show me the peak levels for all my tracks"

**Claude**: "Getting peak levels for all tracks..."

**Track Peak Levels:**
- Track 1 (Drums): -6.2 dB
- Track 2 (Drums): -5.8 dB
- Track 3 (Guitar L): -12.4 dB
- Track 4 (Guitar R): -11.9 dB
- Track 5 (Keys): -15.3 dB
- Track 6 (Lead Vocal): -8.5 dB
- Track 7 (Backing Vocals): -14.2 dB
- Master: -8.2 dB

All tracks have healthy headroom. No peaks above -5 dB.

**You**: "What's the LUFS loudness of my master? I'm targeting -14 LUFS for streaming"

**Claude**: "Measuring integrated loudness on the master bus..."

**Master Loudness Analysis:**
- Integrated LUFS: -14.5 LUFS
- Target: -14.0 LUFS
- Difference: -0.5 LU (slightly under target)

**Loudness Range (LRA):** 8.2 LU (moderately dynamic)

Your mix is very close to streaming target! You're 0.5 LU under -14 LUFS, which is perfect - it leaves a tiny bit of headroom for the streaming platform's encoding process.

---

## Complete Production Workflow

### Full Session from Start to Finish

**You**: "I'm starting a new song. Set up a session for me: create tracks for drums (stereo), bass, two guitars, keys (MIDI), and lead vocal. Set the tempo to 95 BPM and create markers for Intro, Verse, Chorus, and Outro at bars 1, 5, 13, and 25"

**Claude**: "Setting up your complete session structure..."

**Track Creation:**
✓ Created audio track 'Drums L' (track 1)
✓ Created audio track 'Drums R' (track 2)
✓ Created audio track 'Bass' (track 3)
✓ Created audio track 'Guitar 1' (track 4)
✓ Created audio track 'Guitar 2' (track 5)
✓ Created MIDI track 'Keys' (track 6)
✓ Created audio track 'Lead Vocal' (track 7)

**Session Configuration:**
✓ Tempo set to 95 BPM

**Markers:**
✓ Created marker 'Intro' at bar 1
✓ Created marker 'Verse' at bar 5
✓ Created marker 'Chorus' at bar 13
✓ Created marker 'Outro' at bar 25

Your session is ready to go! You have 7 tracks and the song structure marked out.

**You**: "Great! Now arm the bass and both guitars. Set up a loop from the Verse marker to the Chorus marker so I can practice the progression"

**Claude**: "Setting up for rehearsal..."

✓ Armed track 3 (Bass)
✓ Armed track 4 (Guitar 1)
✓ Armed track 5 (Guitar 2)
✓ Loop enabled from bar 5 to bar 13 (Verse to Chorus)

3 tracks armed, loop is set. Ready to rehearse!

**You**: "Let me hear it. Start playing."

**Claude**: "Starting loop playback..."

✓ Transport positioned at bar 5 (Verse marker)
✓ Playback started
✓ Loop: Bar 5 → Bar 13 → Bar 5...

*(Loop plays continuously from Verse to Chorus)*

---

## Troubleshooting and Queries

### Checking Configuration

**You**: "I'm not hearing any sound. What's the status of my tracks?"

**Claude**: "Let me check all your track settings..."

**Track Status Report:**

Track 1 (Drums):
- Muted: No
- Soloed: No
- Gain: -3.0 dB
- Pan: Center
- Record enabled: No
- Input monitoring: Off

Track 6 (Lead Vocal):
- Muted: Yes ⚠️
- Soloed: No
- Gain: -6.0 dB
- Pan: Center
- Record enabled: No
- Input monitoring: Off

**Issue found:** Track 6 (Lead Vocal) is muted! That might be why you're not hearing it.

**You**: "Unmute everything"

**Claude**: "Unmuting all tracks..."

✓ Unmuted all 8 tracks

All tracks are now active and should be audible.

### Session Information

**You**: "What's the current playhead position and transport state?"

**Claude**: "Checking transport status..."

**Transport Information:**
- Position: Bar 12, Beat 3, Frame 48000
- Time: 00:01:32.450
- Playing: Yes
- Recording: No
- Looping: Yes (Bar 5 to Bar 13)
- Tempo: 95 BPM
- Time signature: 4/4

You're currently playing at bar 12 (in the loop), about to hit the Chorus marker.

**You**: "List all my markers"

**Claude**: "Here are all markers in your session..."

**Markers:**
1. Intro - Bar 1, Beat 1
2. Verse - Bar 5, Beat 1
3. Chorus - Bar 13, Beat 1
4. Outro - Bar 25, Beat 1

---

## Tips for Effective Conversations

### Be Natural

You don't need to know the exact tool names or technical commands. Just describe what you want:

❌ "Execute set_track_gain with track_id=3 and gain_db=-6.0"
✅ "Turn down track 3 to -6dB"
✅ "Make the bass quieter"
✅ "Bring up the vocal volume a bit"

### Combine Multiple Actions

You can request complex workflows in a single message:

✅ "Set up for vocal recording: create a track called 'Lead Vocal', arm it, enable input monitoring, add a reverb send at -12dB, and set the loop from bar 8 to bar 16"

### Ask Questions

Don't just command - have a conversation:

✅ "What sends are on the vocal track?"
✅ "Am I clipping anywhere?"
✅ "Which tracks are armed for recording?"
✅ "What's my master level?"

### Use Track Names

If your tracks have descriptive names, use them:

✅ "Mute the drums"
✅ "Pan the guitars hard left and right"
✅ "Add reverb to the vocals"

### Iterate and Refine

If something's not quite right, just say so:

✅ "Actually, make that -8dB instead"
✅ "No, I meant the other guitar track"
✅ "That's too much reverb, bring it down to -18dB"

---

## What Happens Behind the Scenes

When you say: **"Start recording on tracks 1 and 2"**

Claude uses the ardour-mcp tools to:
1. Check if Ardour is connected
2. Verify tracks 1 and 2 exist
3. Call `arm_track(1)` and `arm_track(2)`
4. Call `start_recording()`
5. Report back the results

All through natural conversation - no code required!

---

## Next Steps

- Try these conversations in your own sessions
- Explore the detailed [Usage Examples](USAGE_EXAMPLES.md)
- Read feature-specific guides:
  - [Recording Examples](../RECORDING_EXAMPLE_USAGE.md)
  - [Automation Examples](../AUTOMATION_USAGE.md)
  - [Metering Examples](../METERING_USAGE.md)
  - [Advanced Mixer Examples](../ADVANCED_MIXER_USAGE.md)

Happy producing! 🎵
