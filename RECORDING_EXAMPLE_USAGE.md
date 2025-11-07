# Recording Control Examples

This document provides practical examples for using the Ardour MCP recording control features. These examples demonstrate common recording workflows, punch recording techniques, and monitoring setup.

## Table of Contents

- [Global Recording Control](#global-recording-control)
- [Punch Recording](#punch-recording)
- [Input Monitoring](#input-monitoring)
- [Recording State Queries](#recording-state-queries)
- [Safe Recording Practices](#safe-recording-practices)
- [Complete Workflows](#complete-workflows)

## Global Recording Control

### Start Recording

Start recording with transport playback. This checks that you're not already recording and reports how many tracks are armed.

```python
# Start recording
result = await recording_tools.start_recording()

# Result:
# {
#     "success": True,
#     "message": "Recording started with 2 armed track(s)",
#     "recording": True,
#     "armed_tracks": [1, 3]  # Track IDs that are armed
# }
```

### Stop Recording

Stop recording and transport. Safe to call even if not currently recording.

```python
# Stop recording
result = await recording_tools.stop_recording()

# Result:
# {
#     "success": True,
#     "message": "Recording stopped",
#     "recording": False
# }
```

### Toggle Recording Mode

Toggle the record enable button without starting/stopping transport. Use this to enable record mode before playback.

```python
# Toggle record enable
result = await recording_tools.toggle_recording()

# Result:
# {
#     "success": True,
#     "message": "Record enable toggled",
#     "recording": True
# }
```

### Check Recording Status

Query the current recording state without sending any OSC commands.

```python
# Check if recording
result = await recording_tools.is_recording()

# Result:
# {
#     "success": True,
#     "recording": True,
#     "playing": True,
#     "armed_tracks": [1, 3],
#     "armed_count": 2
# }
```

## Punch Recording

Punch recording allows you to record only within a specific time range, automatically starting and stopping recording at designated points.

### Set Punch Range

Define the punch-in and punch-out points in frames.

```python
# Set punch range from 1 second to 3 seconds (at 48kHz sample rate)
start_frame = 48000   # 1 second at 48kHz
end_frame = 144000    # 3 seconds at 48kHz

result = await recording_tools.set_punch_range(start_frame, end_frame)

# Result:
# {
#     "success": True,
#     "message": "Punch range set: 48000 to 144000",
#     "start_frame": 48000,
#     "end_frame": 144000
# }
```

### Enable Punch-In Mode

Enable automatic recording start at the punch-in point.

```python
# Enable punch-in
result = await recording_tools.enable_punch_in()

# Result:
# {
#     "success": True,
#     "message": "Punch-in enabled"
# }
```

### Enable Punch-Out Mode

Enable automatic recording stop at the punch-out point.

```python
# Enable punch-out
result = await recording_tools.enable_punch_out()

# Result:
# {
#     "success": True,
#     "message": "Punch-out enabled"
# }
```

### Clear Punch Recording

Disable punch recording modes. The punch points are retained but inactive.

```python
# Clear punch recording
result = await recording_tools.clear_punch_range()

# Result:
# {
#     "success": True,
#     "message": "Punch recording disabled"
# }
```

## Input Monitoring

Control how tracks monitor their input signals. Essential for setting up recording sessions.

### Enable Input Monitoring

Monitor the live input signal in real-time.

```python
# Enable input monitoring for track 1
result = await recording_tools.set_input_monitoring(track_id=1, enabled=True)

# Result:
# {
#     "success": True,
#     "message": "Input monitoring enabled for 'Vocals'",
#     "track_id": 1,
#     "track_name": "Vocals",
#     "input_monitoring": True
# }
```

### Enable Disk Monitoring

Monitor the recorded audio from disk (playback mode).

```python
# Enable disk monitoring for track 1
result = await recording_tools.set_disk_monitoring(track_id=1, enabled=True)

# Result:
# {
#     "success": True,
#     "message": "Disk monitoring enabled for 'Vocals'",
#     "track_id": 1,
#     "track_name": "Vocals",
#     "disk_monitoring": True
# }
```

### Set Monitoring Mode

Convenience method to set input, disk, or auto monitoring modes.

```python
# Set to input monitoring (live monitoring)
result = await recording_tools.set_monitoring_mode(track_id=1, mode="input")

# Set to disk monitoring (playback)
result = await recording_tools.set_monitoring_mode(track_id=1, mode="disk")

# Set to auto mode (Ardour manages automatically)
result = await recording_tools.set_monitoring_mode(track_id=1, mode="auto")

# Result:
# {
#     "success": True,
#     "message": "Monitoring mode set to 'input' for 'Vocals'",
#     "track_id": 1,
#     "track_name": "Vocals",
#     "mode": "input"
# }
```

## Recording State Queries

### Get Armed Tracks

List all tracks that are armed for recording.

```python
# Get armed tracks
result = await recording_tools.get_armed_tracks()

# Result:
# {
#     "success": True,
#     "armed_count": 2,
#     "armed_tracks": [
#         {"track_id": 1, "name": "Vocals", "type": "audio"},
#         {"track_id": 3, "name": "Guitar", "type": "audio"}
#     ]
# }
```

### Get Complete Recording State

Get comprehensive recording state including transport, armed tracks, and tempo.

```python
# Get complete recording state
result = await recording_tools.get_recording_state()

# Result:
# {
#     "success": True,
#     "recording": True,
#     "playing": True,
#     "armed_tracks": [1, 3],
#     "armed_count": 2,
#     "tempo": 120.0,
#     "frame": 96000
# }
```

## Safe Recording Practices

### Always Check Before Recording

```python
# Check recording state before starting
status = await recording_tools.is_recording()

if status["recording"]:
    print("Already recording!")
else:
    # Check if any tracks are armed
    armed = await recording_tools.get_armed_tracks()

    if armed["armed_count"] == 0:
        print("Warning: No tracks armed for recording!")
    else:
        print(f"Ready to record on {armed['armed_count']} track(s)")

        # Start recording
        result = await recording_tools.start_recording()
        print(f"Recording started: {result['message']}")
```

### Graceful Recording Stop

```python
# Stop recording safely
result = await recording_tools.stop_recording()

if result["success"]:
    print("Recording stopped successfully")
else:
    print(f"Error stopping recording: {result['error']}")
```

## Complete Workflows

### Basic Recording Session

Complete workflow for a basic recording session.

```python
# 1. Prepare tracks
# Arm tracks for recording using mixer tools
await mixer_tools.set_track_rec_enable(track_id=1, enabled=True)  # Vocals
await mixer_tools.set_track_rec_enable(track_id=3, enabled=True)  # Guitar

# 2. Set up monitoring
# Enable input monitoring for live monitoring
await recording_tools.set_monitoring_mode(track_id=1, mode="input")
await recording_tools.set_monitoring_mode(track_id=3, mode="input")

# 3. Check setup
armed = await recording_tools.get_armed_tracks()
print(f"Ready to record {armed['armed_count']} tracks:")
for track in armed["armed_tracks"]:
    print(f"  - {track['name']} ({track['type']})")

# 4. Start recording
result = await recording_tools.start_recording()
if result["success"]:
    print(f"Recording: {result['message']}")
else:
    print(f"Failed to start: {result['error']}")

# 5. Record your performance...
# (wait for recording to complete)

# 6. Stop recording
result = await recording_tools.stop_recording()
print("Recording stopped")

# 7. Switch to disk monitoring for playback
await recording_tools.set_monitoring_mode(track_id=1, mode="disk")
await recording_tools.set_monitoring_mode(track_id=3, mode="disk")

# 8. Disarm tracks
await mixer_tools.set_track_rec_enable(track_id=1, enabled=False)
await mixer_tools.set_track_rec_enable(track_id=3, enabled=False)
```

### Punch Recording Workflow

Record over a specific section of a track.

```python
# 1. Set up the punch range
# Record from bar 5 to bar 9 (assuming 4/4 time at 120 BPM, 48kHz)
# Each bar = 2 seconds at 120 BPM = 96000 frames at 48kHz

bars_to_frames = 96000  # frames per bar
punch_start = 4 * bars_to_frames  # Start of bar 5
punch_end = 8 * bars_to_frames    # Start of bar 9

result = await recording_tools.set_punch_range(punch_start, punch_end)
print(f"Punch range set: bars 5-9")

# 2. Enable punch-in and punch-out
await recording_tools.enable_punch_in()
await recording_tools.enable_punch_out()

# 3. Arm the track to be punched
await mixer_tools.set_track_rec_enable(track_id=1, enabled=True)

# 4. Set input monitoring for the track
await recording_tools.set_monitoring_mode(track_id=1, mode="input")

# 5. Start playback from before the punch point
# (Use navigation or transport tools to position playhead)
await transport_tools.goto_bar(3)  # Start at bar 3

# 6. Start recording (will punch in/out automatically)
result = await recording_tools.start_recording()
print(f"Punch recording started: {result['message']}")

# 7. Let recording run through punch range...
# (wait for punch-out to happen automatically)

# 8. Stop transport
await recording_tools.stop_recording()

# 9. Clear punch range for next time
await recording_tools.clear_punch_range()

# 10. Reset monitoring
await recording_tools.set_monitoring_mode(track_id=1, mode="disk")
await mixer_tools.set_track_rec_enable(track_id=1, enabled=False)

print("Punch recording complete!")
```

### Multi-Track Overdub Session

Record additional tracks while listening to previously recorded tracks.

```python
# 1. Set up for overdub
# Arm only the new track(s) to record
await mixer_tools.set_track_rec_enable(track_id=4, enabled=True)  # New track

# 2. Ensure previously recorded tracks are NOT armed
await mixer_tools.set_track_rec_enable(track_id=1, enabled=False)
await mixer_tools.set_track_rec_enable(track_id=2, enabled=False)
await mixer_tools.set_track_rec_enable(track_id=3, enabled=False)

# 3. Set monitoring modes
# New track: input monitoring (hear live input)
await recording_tools.set_monitoring_mode(track_id=4, mode="input")

# Existing tracks: disk monitoring (hear playback)
await recording_tools.set_monitoring_mode(track_id=1, mode="disk")
await recording_tools.set_monitoring_mode(track_id=2, mode="disk")
await recording_tools.set_monitoring_mode(track_id=3, mode="disk")

# 4. Check setup
armed = await recording_tools.get_armed_tracks()
assert armed["armed_count"] == 1, "Only one track should be armed"
print(f"Overdubbing on: {armed['armed_tracks'][0]['name']}")

# 5. Position playhead
await transport_tools.goto_start()

# 6. Start recording
result = await recording_tools.start_recording()
print(f"Overdub started: {result['message']}")

# 7. Record...
# (wait for performance)

# 8. Stop recording
await recording_tools.stop_recording()
print("Overdub complete!")

# 9. Clean up
await recording_tools.set_monitoring_mode(track_id=4, mode="disk")
await mixer_tools.set_track_rec_enable(track_id=4, enabled=False)
```

### Recording with Automatic Monitoring

Use auto monitoring mode for most recording scenarios.

```python
# 1. Arm tracks
track_ids = [1, 2, 3]
for track_id in track_ids:
    await mixer_tools.set_track_rec_enable(track_id, enabled=True)

# 2. Set all tracks to auto monitoring
# Ardour will automatically switch between input and disk monitoring
for track_id in track_ids:
    await recording_tools.set_monitoring_mode(track_id, mode="auto")

# 3. Check status
armed = await recording_tools.get_armed_tracks()
print(f"Ready to record {armed['armed_count']} tracks with auto monitoring")

# 4. Record
await recording_tools.start_recording()
# (wait for recording)
await recording_tools.stop_recording()

# 5. Tracks will automatically switch to disk monitoring after recording
print("Recording complete - tracks now in playback mode")
```

## Frame Calculations

Helper examples for calculating frame positions at different sample rates.

```python
# At 48kHz sample rate
sample_rate = 48000

# Convert seconds to frames
seconds = 5.5
frames = int(seconds * sample_rate)  # 264000 frames

# Convert bars to frames (120 BPM, 4/4 time)
bpm = 120
beats_per_bar = 4
seconds_per_beat = 60 / bpm  # 0.5 seconds
seconds_per_bar = seconds_per_beat * beats_per_bar  # 2 seconds
frames_per_bar = int(seconds_per_bar * sample_rate)  # 96000 frames

# Calculate punch range for bars 5-9
start_bar = 5
end_bar = 9
start_frame = (start_bar - 1) * frames_per_bar  # 384000
end_frame = (end_bar - 1) * frames_per_bar      # 768000

await recording_tools.set_punch_range(start_frame, end_frame)
```

## Error Handling

Always check for errors and handle them appropriately.

```python
# Example with error handling
async def safe_start_recording():
    """Start recording with comprehensive error handling."""
    try:
        # Check if already recording
        status = await recording_tools.is_recording()
        if status["recording"]:
            print("Already recording - stop first")
            return False

        # Check for armed tracks
        armed = await recording_tools.get_armed_tracks()
        if armed["armed_count"] == 0:
            print("Warning: No tracks armed!")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False

        # Start recording
        result = await recording_tools.start_recording()

        if result["success"]:
            print(f"Recording started successfully")
            print(f"Armed tracks: {armed['armed_count']}")
            return True
        else:
            print(f"Failed to start recording: {result['error']}")
            return False

    except Exception as e:
        print(f"Error starting recording: {e}")
        return False

# Usage
if await safe_start_recording():
    print("Recording in progress...")
else:
    print("Recording did not start")
```

## Tips and Best Practices

1. **Check State Before Recording**: Always query recording state before starting to avoid conflicts.

2. **Arm Tracks First**: Arm tracks for recording before calling `start_recording()`.

3. **Monitor Setup**: Set up input monitoring on armed tracks so you can hear what you're recording.

4. **Punch Recording**: Use punch recording for precise overdubs without affecting other sections.

5. **Auto Monitoring**: Use `mode="auto"` for most recording sessions - Ardour will manage monitoring automatically.

6. **Frame Calculations**: Calculate frame positions based on your session's sample rate, tempo, and time signature.

7. **Error Handling**: Always check the `success` field in responses and handle errors gracefully.

8. **Clean Up**: After recording, switch tracks to disk monitoring and disarm them to prevent accidental recording.

9. **Transport Control**: Combine recording tools with transport and navigation tools for complete control.

10. **State Queries**: Use query methods (`is_recording()`, `get_armed_tracks()`, `get_recording_state()`) to make informed decisions without sending OSC commands.

## Related Tools

Recording operations work closely with:

- **Mixer Tools**: For arming/disarming tracks (`set_track_rec_enable`, `arm_track_for_recording`, `disarm_track`)
- **Transport Tools**: For playback control during recording
- **Navigation Tools**: For positioning the playhead before recording
- **Session Tools**: For saving sessions after recording

See `MIXER_EXAMPLE_USAGE.md`, `NAVIGATION_EXAMPLE_USAGE.md`, and `ADVANCED_MIXER_USAGE.md` for more details.
