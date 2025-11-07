# Navigation Tools - Example Usage

This document demonstrates the usage of the enhanced navigation functionality added in Phase 2 of the Ardour MCP project.

## Overview

The NavigationTools class provides comprehensive navigation control for Ardour, including:
- Marker management (create, delete, rename, goto, query)
- Loop control (set range, enable/disable)
- Tempo and time signature control
- Navigation helpers (goto time, bar, skip forward/backward)

## Prerequisites

```python
from ardour_mcp.tools.navigation import NavigationTools
from ardour_mcp.osc_bridge import ArdourOSCBridge
from ardour_mcp.ardour_state import ArdourState

# Initialize components
osc_bridge = ArdourOSCBridge(host="localhost", port=3819)
state = ArdourState()
await osc_bridge.connect()

# Create navigation tools instance
nav = NavigationTools(osc_bridge, state)
```

## Marker Management

### Create a Marker

```python
# Create marker at current position
result = await nav.create_marker("Verse 1")
print(result)
# {'success': True, 'marker_name': 'Verse 1', 'message': 'Created marker...'}

# Create marker at specific position (frame 480000)
result = await nav.create_marker("Chorus", position=480000)
print(result)
# {'success': True, 'marker_name': 'Chorus', 'position': 480000, 'message': 'Created marker...'}
```

### Delete a Marker

```python
result = await nav.delete_marker("Verse 1")
print(result)
# {'success': True, 'marker_name': 'Verse 1', 'message': "Deleted marker 'Verse 1'"}
```

### Rename a Marker

```python
result = await nav.rename_marker("Verse", "Verse 1")
print(result)
# {'success': True, 'old_name': 'Verse', 'new_name': 'Verse 1', 'message': "Renamed marker..."}
```

### Jump to a Marker

```python
result = await nav.goto_marker("Chorus")
print(result)
# {'success': True, 'marker_name': 'Chorus', 'message': "Jumped to marker 'Chorus'"}
```

### Get Marker Position

```python
result = await nav.get_marker_position("Verse 1")
print(result)
# {'success': True, 'marker_name': 'Verse 1', 'position': 240000, 'message': "Marker 'Verse 1' is at frame 240000"}
```

## Loop Control

### Set Loop Range

```python
# Set loop from frame 48000 to 96000
result = await nav.set_loop_range(48000, 96000)
print(result)
# {'success': True, 'loop_start': 48000, 'loop_end': 96000, 'message': 'Loop range set: 48000 to 96000'}
```

### Enable Loop Playback

```python
result = await nav.enable_loop()
print(result)
# {'success': True, 'loop_enabled': True, 'message': 'Loop enabled'}
```

### Disable Loop Playback

```python
result = await nav.disable_loop()
print(result)
# {'success': True, 'loop_enabled': False, 'message': 'Loop disabled'}
```

### Clear Loop Range

```python
result = await nav.clear_loop_range()
print(result)
# {'success': True, 'loop_enabled': False, 'message': 'Loop range cleared'}
```

## Tempo and Time Signature

### Set Tempo

```python
# Set tempo to 140 BPM
result = await nav.set_tempo(140.0)
print(result)
# {'success': True, 'tempo': 140.0, 'message': 'Tempo set to 140.0 BPM'}

# Tempo must be between 20.0 and 300.0 BPM
```

### Get Current Tempo

```python
result = await nav.get_tempo()
print(result)
# {'success': True, 'tempo': 120.0, 'message': 'Current tempo: 120.0 BPM'}
```

### Set Time Signature

```python
# Set to 3/4 time
result = await nav.set_time_signature(3, 4)
print(result)
# {'success': True, 'time_signature': '3/4', 'message': 'Time signature set to 3/4'}

# Set to 6/8 time
result = await nav.set_time_signature(6, 8)
print(result)
# {'success': True, 'time_signature': '6/8', 'message': 'Time signature set to 6/8'}

# Valid denominators: 1, 2, 4, 8, 16, 32
# Valid numerators: 1-32
```

### Get Current Time Signature

```python
result = await nav.get_time_signature()
print(result)
# {'success': True, 'time_signature': '4/4', 'numerator': 4, 'denominator': 4, 'message': 'Current time signature: 4/4'}
```

## Navigation Helpers

### Jump to Timecode

```python
# Jump to 1 minute, 30 seconds
result = await nav.goto_time(hours=0, minutes=1, seconds=30, frames=0)
print(result)
# {'success': True, 'timecode': '00:01:30:00', 'frame': 4320000, 'message': 'Jumped to timecode 00:01:30:00'}

# Jump to 2 hours, 15 minutes, 45 seconds
result = await nav.goto_time(2, 15, 45, 0)
print(result)
# {'success': True, 'timecode': '02:15:45:00', 'frame': 390240000, 'message': 'Jumped to timecode 02:15:45:00'}
```

### Jump to Bar Number

```python
# Jump to bar 5
result = await nav.goto_bar(5)
print(result)
# {'success': True, 'bar': 5, 'frame': 384000, 'message': 'Jumped to bar 5'}

# Note: Bar calculation uses current tempo and time signature
# At 120 BPM, 4/4 time: bar 5 = (5-1) * 4 beats * 0.5 sec/beat * 48000 samples/sec = 384000 frames
```

### Skip Forward

```python
# Skip forward 10 seconds
result = await nav.skip_forward(10.0)
print(result)
# {'success': True, 'seconds': 10.0, 'frame': 528000, 'message': 'Skipped forward 10.0 seconds'}
```

### Skip Backward

```python
# Skip backward 5 seconds
result = await nav.skip_backward(5.0)
print(result)
# {'success': True, 'seconds': 5.0, 'frame': 288000, 'message': 'Skipped backward 5.0 seconds'}

# Note: Will not go below frame 0
```

## Complete Workflow Example

```python
async def arrange_song_workflow():
    """Example workflow for arranging a song with markers and loops."""

    # Create song structure markers
    await nav.create_marker("Intro", 0)
    await nav.create_marker("Verse 1", 192000)
    await nav.create_marker("Chorus", 576000)
    await nav.create_marker("Verse 2", 960000)
    await nav.create_marker("Bridge", 1344000)
    await nav.create_marker("Final Chorus", 1728000)
    await nav.create_marker("Outro", 2112000)

    # Set tempo for the intro section
    await nav.goto_marker("Intro")
    await nav.set_tempo(110.0)

    # Loop the chorus for practice
    await nav.goto_marker("Chorus")
    start_frame = (await nav.get_marker_position("Chorus"))["position"]
    await nav.goto_marker("Verse 2")
    end_frame = (await nav.get_marker_position("Verse 2"))["position"]
    await nav.set_loop_range(start_frame, end_frame)
    await nav.enable_loop()

    # ... do work on chorus ...

    # Disable loop and continue
    await nav.disable_loop()

    # Speed up tempo for the bridge
    await nav.goto_marker("Bridge")
    await nav.set_tempo(130.0)

    # Quick navigation: skip to 30 seconds before the end
    await nav.goto_marker("Outro")
    await nav.skip_backward(30.0)

    # Return to the start
    await nav.goto_time(0, 0, 0, 0)

    print("Song arrangement complete!")

# Run the workflow
await arrange_song_workflow()
```

## Error Handling

All navigation methods return dictionaries with a `success` field:

```python
result = await nav.create_marker("Test")

if result["success"]:
    print(f"Success: {result['message']}")
else:
    print(f"Error: {result['error']}")
```

Common error scenarios:
- **Not connected**: OSC bridge is not connected to Ardour
- **Invalid parameters**: Out-of-range values (tempo, frames, etc.)
- **Marker not found**: Attempting to access a non-existent marker
- **OSC command failure**: Command could not be sent or executed

## MCP Server Integration

When using the MCP server, these tools are registered as:

**Marker Management:**
- `create_marker(name, position?)`
- `delete_marker(name)`
- `rename_marker(old_name, new_name)`
- `goto_marker_by_name(name)`
- `get_marker_position(name)`

**Loop Control:**
- `set_loop_range_frames(start_frame, end_frame)`
- `enable_loop()`
- `disable_loop()`
- `clear_loop_range()`

**Tempo & Time Signature:**
- `set_session_tempo(bpm)`
- `get_session_tempo()`
- `set_session_time_signature(numerator, denominator)`
- `get_session_time_signature()`

**Navigation Helpers:**
- `goto_timecode(hours, minutes, seconds, frames?)`
- `goto_bar_number(bar_number)`
- `skip_forward_seconds(seconds)`
- `skip_backward_seconds(seconds)`

## Advanced Tips

### Frame Conversion

The NavigationTools class includes helper methods for converting between different time representations:

```python
# Convert timecode to frames (internal helper)
frames = nav._timecode_to_frames(0, 1, 30, 0)  # 1:30 = 4320000 frames at 48kHz

# Convert bar number to frames (internal helper)
frames = nav._bar_to_frames(5)  # Bar 5 position based on tempo/time sig
```

### Sample Rate Awareness

All frame calculations use the session's sample rate from the cached state:
- Default: 48000 Hz
- Common rates: 44100 Hz, 48000 Hz, 96000 Hz, 192000 Hz

### Tempo Map Considerations

The navigation helpers (goto_bar, timecode conversion) use the current global tempo and time signature. For sessions with tempo automation or multiple tempo changes, these calculations provide approximate positions.

## See Also

- Transport Tools: For playback control (play, stop, record)
- Session Tools: For session information and management
- Mixer Tools: For track volume, pan, and routing
- Track Tools: For track creation and management
