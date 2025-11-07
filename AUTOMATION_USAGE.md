# Automation Control Usage Guide

This guide covers the automation control features of Ardour MCP, allowing you to control parameter automation modes, recording, editing, and playback.

## Overview

Automation in Ardour allows you to record and play back parameter changes over time. The automation control tools provide comprehensive control over:

- **Automation Modes**: Control how automation data is played back and recorded
- **Automation Recording**: Record automation data for specific parameters
- **Automation Editing**: Clear and copy automation data
- **Automation Playback**: Enable/disable automation playback

## Automation Modes

### Available Modes

Ardour supports five automation modes:

1. **off** - Automation disabled, manual control only
2. **play** - Play back existing automation data
3. **write** - Overwrite automation data during playback
4. **touch** - Write automation only when control is touched
5. **latch** - Write automation from touch point until playback stops

### Set Automation Mode

Set the automation mode for a specific parameter on a track.

```python
# Set gain automation to write mode
result = await set_automation_mode(
    track_id=1,
    parameter="gain",
    mode="write"
)

# Set pan automation to play mode
result = await set_automation_mode(
    track_id=2,
    parameter="pan",
    mode="play"
)

# Disable mute automation
result = await set_automation_mode(
    track_id=3,
    parameter="mute",
    mode="off"
)
```

**Parameters:**
- `track_id` (int): Track strip ID (1-based)
- `parameter` (str): Parameter name ("gain", "pan", "mute", "plugin")
- `mode` (str): Automation mode (off/play/write/touch/latch)

**Returns:**
```json
{
  "success": true,
  "track_id": 1,
  "track_name": "Vocals",
  "parameter": "gain",
  "mode": "write",
  "message": "Set gain automation mode to 'write' on track 'Vocals'"
}
```

### Get Automation Mode

Query the current automation mode for a parameter.

```python
# Get current gain automation mode
result = await get_automation_mode(
    track_id=1,
    parameter="gain"
)
```

**Note:** Automation mode is not currently cached in the state system.

### List Automation Parameters

Get a list of available automation parameters for a track.

```python
# List automatable parameters
result = await list_automation_parameters(track_id=1)
```

**Returns:**
```json
{
  "success": true,
  "track_id": 1,
  "track_name": "Vocals",
  "parameters": ["gain", "pan", "mute"],
  "message": "Automation parameters for track 'Vocals'"
}
```

## Automation Recording

### Enable Write Mode for All Parameters

Enable automation write mode for all parameters on a track.

```python
# Enable write mode for all parameters
result = await enable_automation_write(track_id=1)
```

This sets all automatable parameters to write mode, allowing you to record automation data during playback.

### Disable Write Mode for All Parameters

Disable automation write mode and return to play mode.

```python
# Disable write mode, return to play mode
result = await disable_automation_write(track_id=1)
```

### Record Automation for Specific Parameter

Start recording automation for a specific parameter.

```python
# Start recording gain automation
result = await record_automation(
    track_id=1,
    parameter="gain"
)

# Start recording pan automation
result = await record_automation(
    track_id=2,
    parameter="pan"
)
```

This is equivalent to calling `set_automation_mode(track_id, parameter, "write")`.

### Stop Automation Recording

Stop recording automation for a specific parameter.

```python
# Stop recording gain automation
result = await stop_automation_recording(
    track_id=1,
    parameter="gain"
)
```

This sets the parameter to play mode, preserving existing automation while stopping new recording.

## Automation Editing

### Clear Automation

Clear automation data for a parameter.

```python
# Clear all gain automation on track 1
result = await clear_automation(
    track_id=1,
    parameter="gain"
)

# Clear automation in a specific frame range
result = await clear_automation(
    track_id=1,
    parameter="gain",
    start_frame=1000,
    end_frame=5000
)
```

**Parameters:**
- `track_id` (int): Track strip ID (1-based)
- `parameter` (str): Parameter name
- `start_frame` (int, optional): Start frame for range (None = clear all)
- `end_frame` (int, optional): End frame for range (None = clear all)

**Note:** Ardour's OSC interface has limited automation editing support. The implementation sets automation mode to "off" as a basic approach to clearing.

### Check if Automation Exists

Check whether automation data exists for a parameter.

```python
# Check if gain automation exists
result = await has_automation(
    track_id=1,
    parameter="gain"
)
```

**Note:** Automation existence is not currently cached in the state system.

### Copy Automation Between Tracks

Copy automation data from one track to another.

```python
# Copy gain automation from track 1 to track 2
result = await copy_automation(
    source_track=1,
    dest_track=2,
    parameter="gain"
)
```

**Note:** Direct automation copying is not supported via OSC and typically requires GUI interaction. This method provides an informational response.

## Automation Playback

### Enable Automation Playback

Enable playback of automation data for a parameter.

```python
# Enable gain automation playback
result = await enable_automation_playback(
    track_id=1,
    parameter="gain"
)
```

This sets the parameter to play mode, enabling playback without recording.

### Disable Automation Playback

Disable automation playback for a parameter.

```python
# Disable gain automation playback
result = await disable_automation_playback(
    track_id=1,
    parameter="gain"
)
```

This sets the parameter to off mode, disabling both playback and recording.

### Get Complete Automation State

Get comprehensive automation status for a parameter.

```python
# Get automation state for gain
result = await get_automation_state(
    track_id=1,
    parameter="gain"
)
```

**Returns:**
```json
{
  "success": true,
  "track_id": 1,
  "track_name": "Vocals",
  "parameter": "gain",
  "mode": null,
  "has_automation": null,
  "playback_enabled": null,
  "message": "Automation state for gain on track 'Vocals' (not cached)"
}
```

**Note:** Automation state is not currently cached. Future versions may provide real-time state information.

## Common Workflows

### Recording Gain Automation

```python
# 1. Enable gain automation recording
await record_automation(track_id=1, parameter="gain")

# 2. Start playback and adjust gain
# (perform manual adjustments during playback)

# 3. Stop automation recording
await stop_automation_recording(track_id=1, parameter="gain")

# 4. Enable playback to hear the automation
await enable_automation_playback(track_id=1, parameter="gain")
```

### Touch Recording Workflow

```python
# 1. Set to touch mode - only records when you move the control
await set_automation_mode(track_id=1, parameter="gain", mode="touch")

# 2. Start playback and touch controls as needed
# Automation is only written when you actively adjust the parameter

# 3. Return to play mode to hear the result
await set_automation_mode(track_id=1, parameter="gain", mode="play")
```

### Clearing and Re-recording

```python
# 1. Clear existing automation
await clear_automation(track_id=1, parameter="pan")

# 2. Record new automation
await record_automation(track_id=1, parameter="pan")

# 3. Perform adjustments during playback

# 4. Stop recording and enable playback
await stop_automation_recording(track_id=1, parameter="pan")
await enable_automation_playback(track_id=1, parameter="pan")
```

### Batch Operations Across Tracks

```python
# Enable write mode on multiple tracks
for track_id in [1, 2, 3]:
    await enable_automation_write(track_id)

# Record automation during performance

# Disable write mode on all tracks
for track_id in [1, 2, 3]:
    await disable_automation_write(track_id)
```

## Parameter Reference

### Common Automatable Parameters

- **gain** - Track volume/gain fader
- **pan** - Stereo pan position
- **mute** - Track mute state
- **plugin** - Plugin parameters (specific to installed plugins)

### OSC Command Reference

The automation tools use the following OSC commands:

- `/strip/{parameter}/automation_mode isi strip_id mode_value`
  - Mode values: 0=off, 1=play, 2=write, 3=touch, 4=latch
- `/strip/automation_mode isi strip_id mode_value`
  - Sets mode for all parameters

## Tips and Best Practices

1. **Use Touch Mode for Subtle Adjustments**: Touch mode is ideal when you want to preserve most of the existing automation but make small changes.

2. **Latch Mode for Extended Changes**: Use latch mode when you need to make changes that continue after you release the control.

3. **Enable Playback After Recording**: Always set the mode to "play" after recording to hear your automation changes.

4. **Clear Before Re-recording**: If you're unhappy with automation, clear it completely before trying again.

5. **Use Write Mode Carefully**: Write mode overwrites all automation during playback, even if you don't touch the control. Use touch or latch mode for safer recording.

6. **Check Parameters Before Recording**: Use `list_automation_parameters()` to see what's available for each track.

## Limitations

Due to Ardour's OSC interface capabilities:

- Automation state is not cached and requires live queries
- Range-based automation clearing has limited support
- Automation copying between tracks is not directly supported via OSC
- Plugin parameter automation requires knowledge of plugin structure

## Error Handling

All automation functions return a result dictionary with a `success` field:

```python
result = await set_automation_mode(1, "gain", "write")

if result["success"]:
    print(f"Success: {result['message']}")
else:
    print(f"Error: {result['error']}")
```

Common errors:
- "Not connected to Ardour" - OSC connection not established
- "Track not found" - Invalid track ID
- "Invalid mode" - Unsupported automation mode
- "Invalid parameter" - Parameter name not recognized
- "Failed to send OSC command" - Communication failure

## See Also

- [Mixer Control Guide](MIXER_USAGE.md) - Track mixer controls
- [Recording Guide](RECORDING_USAGE.md) - Recording control features
- [Ardour OSC Documentation](https://manual.ardour.org/using-control-surfaces/controlling-ardour-with-osc/)
