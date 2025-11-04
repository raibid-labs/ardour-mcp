# Ardour OSC API Reference

Complete reference for Ardour's Open Sound Control (OSC) API. This document lists all OSC commands and feedback messages used by Ardour MCP.

## OSC Basics

### Protocol

- **Transport**: UDP (User Datagram Protocol)
- **Default Port**: 3819 (Ardour server)
- **Feedback Port**: Configurable (default: 3820)
- **Address Pattern**: `/path/to/command`
- **Type Tags**: `i` (int), `f` (float), `s` (string), `b` (blob)

### Message Format

```
/address/pattern <type-tag> <value1> <value2> ...

Example:
/strip/gain 1 f -6.0
```

## Transport Control

### Commands (Ardour receives)

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/transport_play` | - | - | Start playback |
| `/transport_stop` | - | - | Stop playback |
| `/transport_pause` | - | - | Toggle pause |
| `/rec_enable_toggle` | - | - | Toggle global record enable |
| `/toggle_roll` | - | - | Toggle play/stop |
| `/goto_start` | - | - | Go to session start |
| `/goto_end` | - | - | Go to session end |
| `/rewind` | - | - | Fast rewind |
| `/ffwd` | - | - | Fast forward |
| `/set_transport_speed` | `f` | speed | Set transport speed (-1.0 to 1.0) |
| `/locate` | `i` | frame | Jump to frame position |
| `/loop_toggle` | - | - | Toggle loop mode |
| `/set_loop_range` | `ii` | start, end | Set loop range (frames) |
| `/toggle_punch_in` | - | - | Toggle punch-in recording |
| `/toggle_punch_out` | - | - | Toggle punch-out recording |

### Feedback (Ardour sends)

| Message | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/transport_frame` | `i` | frame | Current playback frame |
| `/transport_speed` | `f` | speed | Current transport speed |
| `/record_enabled` | `i` | enabled | Global record enable (0/1) |
| `/loop_toggle` | `i` | enabled | Loop mode enabled (0/1) |
| `/punch_in` | `i` | enabled | Punch-in enabled (0/1) |
| `/punch_out` | `i` | enabled | Punch-out enabled (0/1) |

## Session Information

### Commands

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/refresh` | - | - | Request full state refresh |
| `/save_state` | - | - | Save session |

### Feedback

| Message | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/session_name` | `s` | name | Session name |
| `/sample_rate` | `i` | rate | Session sample rate (Hz) |
| `/tempo` | `f` | bpm | Current tempo (BPM) |
| `/time_signature` | `ii` | beats, beat_type | Time signature (e.g., 4/4) |
| `/n_tracks` | `i` | count | Number of tracks |
| `/dirty` | `i` | dirty | Session modified since save (0/1) |

## Track/Strip Control

Ardour uses "strip" to refer to tracks and busses. Strip IDs are 1-based.

### Commands

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/strip/list` | - | - | Request track list |
| `/strip/name` | `is` | strip_id, name | Set track name |
| `/strip/gain` | `if` | strip_id, gain_db | Set track gain (-inf to +6dB) |
| `/strip/fader` | `if` | strip_id, position | Set fader position (0.0 to 1.0) |
| `/strip/pan_stereo_position` | `if` | strip_id, position | Set pan position (-1.0 to 1.0) |
| `/strip/mute` | `if` | strip_id, mute | Mute track (0=unmute, 1=mute) |
| `/strip/solo` | `if` | strip_id, solo | Solo track (0=unsolo, 1=solo) |
| `/strip/recenable` | `if` | strip_id, enable | Arm track for recording (0/1) |
| `/strip/monitor_input` | `if` | strip_id, enable | Monitor input (0/1) |
| `/strip/monitor_disk` | `if` | strip_id, enable | Monitor disk (0/1) |
| `/strip/select` | `ii` | strip_id, select | Select track (0/1) |
| `/strip/hide` | `ii` | strip_id, hide | Hide track (0/1) |

### Feedback

| Message | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/strip/name` | `is` | strip_id, name | Track name |
| `/strip/gain` | `if` | strip_id, gain_db | Track gain (dB) |
| `/strip/fader` | `if` | strip_id, position | Fader position |
| `/strip/pan_stereo_position` | `if` | strip_id, position | Pan position |
| `/strip/mute` | `ii` | strip_id, mute | Mute state (0/1) |
| `/strip/solo` | `ii` | strip_id, solo | Solo state (0/1) |
| `/strip/recenable` | `ii` | strip_id, enable | Record arm state (0/1) |
| `/strip/monitor_input` | `ii` | strip_id, enable | Monitor input (0/1) |
| `/strip/monitor_disk` | `ii` | strip_id, enable | Monitor disk (0/1) |

## Track Creation

### Commands

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/add_audio_track` | `i` | count | Add audio track(s) |
| `/add_midi_track` | `i` | count | Add MIDI track(s) |
| `/remove_strip` | `i` | strip_id | Remove track/bus |

## Mixer Operations

### Send Control

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/strip/send/gain` | `iif` | strip_id, send_id, gain_db | Set send gain |
| `/strip/send/fader` | `iif` | strip_id, send_id, position | Set send fader |
| `/strip/send/enable` | `iii` | strip_id, send_id, enable | Enable send (0/1) |

### Plugin Control

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/strip/plugin/parameter` | `iiif` | strip_id, plugin_id, param_id, value | Set plugin parameter |
| `/strip/plugin/activate` | `iii` | strip_id, plugin_id, activate | Activate plugin (0/1) |

## Markers

### Commands

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/add_marker` | `s` | name | Add marker at current position |
| `/add_marker` | `is` | frame, name | Add marker at specific frame |
| `/remove_marker` | `s` | name | Remove marker by name |
| `/locate` | `s` | marker_name | Jump to marker |

### Feedback

| Message | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/marker` | `is` | frame, name | Marker position and name |

## Automation

### Commands

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/strip/gain/automation` | `ii` | strip_id, mode | Set gain automation mode |
| `/strip/pan/automation` | `ii` | strip_id, mode | Set pan automation mode |

**Automation Modes:**
- `0`: Manual
- `1`: Play
- `2`: Write
- `3`: Touch

## Selection

### Commands

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/select/strip` | `i` | strip_id | Select specific strip |
| `/select/gain` | `f` | gain_db | Set selected strip gain |
| `/select/pan` | `f` | position | Set selected strip pan |
| `/select/mute` | `i` | mute | Mute selected strip (0/1) |
| `/select/solo` | `i` | solo | Solo selected strip (0/1) |

### Feedback

| Message | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/select/strip_id` | `i` | strip_id | Currently selected strip |
| `/select/name` | `s` | name | Selected strip name |

## Cue Control (Ardour 8.x)

### Commands

| Command | Type Tags | Args | Description |
|---------|-----------|------|-------------|
| `/cue/fire` | `i` | cue_id | Trigger cue |
| `/cue/stop` | `i` | cue_id | Stop cue |
| `/cue/load` | `ii` | bank, cue_id | Load cue to bank |

## Custom Commands

Ardour also supports user-defined OSC commands via Lua scripts.

## OSC Configuration in Ardour

### Preferences

**Edit → Preferences → Control Surfaces → Open Sound Control (OSC)**

Settings:
- **OSC Server Port**: Port Ardour listens on (default: 3819)
- **Feedback**: Enable/configure feedback messages
- **Gain Mode**: dB or Fader (0.0-1.0)
- **Debug Mode**: Enable OSC message logging
- **Default Strip Types**: Audio, MIDI, Busses, VCAs
- **Default Feedback**: Choose feedback categories
- **Bank Size**: Number of strips in a bank (0 = unlimited)

### Feedback Options

Enable desired feedback:
- ✅ **Transport**: Playback position, speed, record state
- ✅ **Strips**: Track/bus parameters
- ✅ **Metering**: Level meters (can be high bandwidth)
- ✅ **Timecode**: SMPTE timecode
- ✅ **Selection**: Selected strip changes
- ✅ **Heartbeat**: Periodic connection check

## Error Handling

### Common Errors

- **Invalid strip ID**: No response (silently ignored)
- **Invalid parameter value**: May be clamped to valid range
- **Unknown command**: Silently ignored
- **Network errors**: No explicit error messages

### Best Practices

1. **Validate inputs** before sending commands
2. **Use feedback** to verify command execution
3. **Implement timeouts** for feedback (1-2 seconds)
4. **Handle missing feedback** gracefully
5. **Refresh state** periodically to stay synchronized

## Testing OSC Commands

### Using Python

```python
from pythonosc import udp_client

# Create client
client = udp_client.SimpleUDPClient("127.0.0.1", 3819)

# Send commands
client.send_message("/transport_play", [])
client.send_message("/strip/gain", [1, -6.0])
client.send_message("/strip/name", [1, "Vocals"])
```

### Using osculator or OSC Testing Tools

Many GUI and CLI tools exist for testing OSC:
- **osculator** (macOS)
- **OSCTest** (cross-platform)
- **TouchOSC** (mobile)
- **Pure Data** with OSC objects
- **Max/MSP** with OSC objects

## Performance Considerations

### Command Latency

- Typical latency: 1-10ms for local connections
- Network latency: Depends on network conditions
- Ardour processing: Usually < 1ms

### Feedback Rate

- Transport feedback: ~30-60 Hz
- Metering feedback: Up to 20 Hz (configurable, can be intensive)
- Parameter feedback: On change only

### Bandwidth

- Commands: Low bandwidth (< 1KB/s typical)
- Feedback: Can be high with metering enabled (up to 100KB/s)
- Recommendation: Disable metering feedback if not needed

## Version Compatibility

This reference is based on **Ardour 8.x**. Earlier versions may have different commands or behavior.

### Version Differences

- **Ardour 7.x**: Most commands compatible, some cue commands missing
- **Ardour 6.x**: Fewer automation options, different plugin addressing
- **Ardour 5.x and earlier**: Significant differences, not recommended

## Resources

- [Official Ardour OSC Documentation](https://manual.ardour.org/using-control-surfaces/controlling-ardour-with-osc/)
- [OSC Specification](http://opensoundcontrol.org/spec-1_0)
- [python-osc Documentation](https://python-osc.readthedocs.io/)

---

This reference covers the most commonly used OSC commands. For a complete list, consult the [official Ardour manual](https://manual.ardour.org/).
