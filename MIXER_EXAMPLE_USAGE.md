# Mixer Tools - Example Usage

This document demonstrates how to use the newly implemented mixer control functionality.

## Overview

The MixerTools class provides 14 comprehensive methods for controlling Ardour's mixer:

### Individual Track Controls
1. `set_track_volume(track_id, volume_db)` - Set track gain (-193.0 to +6.0 dB)
2. `set_track_pan(track_id, pan)` - Set stereo pan (-1.0 to +1.0)
3. `set_track_mute(track_id, muted)` - Mute/unmute a track
4. `toggle_track_mute(track_id)` - Toggle mute state
5. `set_track_solo(track_id, soloed)` - Solo/unsolo a track
6. `toggle_track_solo(track_id)` - Toggle solo state
7. `set_track_rec_enable(track_id, enabled)` - Arm/disarm for recording
8. `toggle_track_rec_enable(track_id)` - Toggle rec enable state

### Convenience Methods
9. `arm_track_for_recording(track_id)` - Arm track (convenience)
10. `disarm_track(track_id)` - Disarm track (convenience)

### Batch Operations
11. `mute_all_tracks()` - Mute all tracks in session
12. `unmute_all_tracks()` - Unmute all tracks in session
13. `clear_all_solos()` - Clear solo from all tracks

### Query Methods
14. `get_track_mixer_state(track_id)` - Get all mixer parameters for a track

## Example Usage

### Setting Volume

```python
# Set track 1 to -6dB
result = await mixer_tools.set_track_volume(1, -6.0)
# Returns:
# {
#     "success": True,
#     "message": "Set volume for track 'Vocals' to -6.0dB",
#     "track_id": 1,
#     "track_name": "Vocals",
#     "volume_db": -6.0
# }

# Volume range: -193.0 (silent) to +6.0 (max boost)
```

### Setting Pan

```python
# Pan track 2 to 50% left
result = await mixer_tools.set_track_pan(2, -0.5)
# Returns:
# {
#     "success": True,
#     "message": "Set pan for track 'Guitar' to 50% left",
#     "track_id": 2,
#     "track_name": "Guitar",
#     "pan": -0.5
# }

# Pan range: -1.0 (hard left) to +1.0 (hard right), 0.0 = center
```

### Muting Tracks

```python
# Mute a specific track
result = await mixer_tools.set_track_mute(3, True)

# Toggle mute state (uses cached state to determine current state)
result = await mixer_tools.toggle_track_mute(3)

# Mute all tracks in session
result = await mixer_tools.mute_all_tracks()
# Returns:
# {
#     "success": True,
#     "message": "Muted 5/5 tracks",
#     "tracks_muted": 5,
#     "total_tracks": 5
# }
```

### Solo Operations

```python
# Solo a track
result = await mixer_tools.set_track_solo(4, True)

# Clear all solos (returns to normal monitoring)
result = await mixer_tools.clear_all_solos()
# Returns:
# {
#     "success": True,
#     "message": "Cleared solo on 5/5 tracks",
#     "tracks_unsoloed": 5,
#     "total_tracks": 5
# }
```

### Recording Arm

```python
# Arm track 1 for recording
result = await mixer_tools.arm_track_for_recording(1)

# Toggle rec enable
result = await mixer_tools.toggle_track_rec_enable(1)

# Disarm track
result = await mixer_tools.disarm_track(1)
```

### Query Mixer State

```python
# Get complete mixer state for a track
result = await mixer_tools.get_track_mixer_state(1)
# Returns:
# {
#     "success": True,
#     "track_id": 1,
#     "track_name": "Vocals",
#     "track_type": "audio",
#     "gain_db": -6.0,
#     "pan": 0.0,
#     "muted": False,
#     "soloed": False,
#     "rec_enabled": True
# }
```

## Error Handling

All methods include robust error handling:

### Connection Errors
```python
# When not connected to Ardour
result = await mixer_tools.set_track_volume(1, -6.0)
# Returns: {"success": False, "error": "Not connected to Ardour"}
```

### Track Not Found
```python
# When track ID doesn't exist
result = await mixer_tools.set_track_volume(99, -6.0)
# Returns: {"success": False, "error": "Track 99 not found"}
```

### Range Validation
```python
# Volume out of range
result = await mixer_tools.set_track_volume(1, -200.0)
# Returns: {"success": False, "error": "Volume -200.0dB out of range (-193.0 to +6.0)"}

# Pan out of range
result = await mixer_tools.set_track_pan(1, 1.5)
# Returns: {"success": False, "error": "Pan 1.5 out of range (-1.0 to +1.0)"}
```

### Batch Operation Failures
```python
# When some tracks fail during batch operation
result = await mixer_tools.mute_all_tracks()
# Returns:
# {
#     "success": False,
#     "message": "Muted 4/5 tracks",
#     "tracks_muted": 4,
#     "total_tracks": 5,
#     "failed_tracks": [3]  # List of track IDs that failed
# }
```

## Integration with MCP Server

All mixer methods are registered as MCP tools and can be called via the MCP protocol:

- `set_track_volume(track_id: int, volume_db: float)`
- `set_track_pan(track_id: int, pan: float)`
- `set_track_mute(track_id: int, muted: bool)`
- `toggle_track_mute(track_id: int)`
- `set_track_solo(track_id: int, soloed: bool)`
- `toggle_track_solo(track_id: int)`
- `set_track_rec_enable(track_id: int, enabled: bool)`
- `toggle_track_rec_enable(track_id: int)`
- `arm_track_for_recording(track_id: int)`
- `disarm_track(track_id: int)`
- `mute_all_tracks()`
- `unmute_all_tracks()`
- `clear_all_solos()`
- `get_track_mixer_state(track_id: int)`

## Common Workflows

### Recording Setup
```python
# 1. Unmute all tracks to reset
await mixer_tools.unmute_all_tracks()

# 2. Clear any solos
await mixer_tools.clear_all_solos()

# 3. Arm specific tracks for recording
await mixer_tools.arm_track_for_recording(1)  # Vocals
await mixer_tools.arm_track_for_recording(2)  # Guitar

# 4. Set monitoring levels
await mixer_tools.set_track_volume(1, -6.0)  # Lower vocal level
await mixer_tools.set_track_volume(2, -3.0)  # Lower guitar level
```

### Mixing Session
```python
# 1. Solo a track to focus on it
await mixer_tools.set_track_solo(1, True)

# 2. Adjust its pan and volume
await mixer_tools.set_track_pan(1, -0.3)  # Slightly left
await mixer_tools.set_track_volume(1, -6.0)

# 3. Check current mixer state
state = await mixer_tools.get_track_mixer_state(1)

# 4. Clear solo to hear in context
await mixer_tools.clear_all_solos()
```

### Quick Mute/Unmute
```python
# Mute all tracks for a clean slate
await mixer_tools.mute_all_tracks()

# Unmute specific tracks to build the mix
await mixer_tools.set_track_mute(1, False)  # Vocals
await mixer_tools.set_track_mute(4, False)  # Drums
await mixer_tools.set_track_mute(5, False)  # Bass

# Or unmute everything
await mixer_tools.unmute_all_tracks()
```

## OSC Commands Reference

All mixer operations use Ardour's OSC protocol:

- `/strip/gain if` - Set track gain (track_id, gain_db)
- `/strip/pan_stereo_position if` - Set pan (track_id, position)
- `/strip/mute ii` - Set mute (track_id, 1=muted/0=unmuted)
- `/strip/solo ii` - Set solo (track_id, 1=soloed/0=unsoloed)
- `/strip/recenable ii` - Set rec enable (track_id, 1=armed/0=disarmed)

All commands require an active OSC connection to Ardour.
