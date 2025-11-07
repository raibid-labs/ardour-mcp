# Advanced Mixer Usage Guide

This guide demonstrates how to use the advanced mixer tools in the Ardour MCP project. These tools provide control over sends, plugins, buses, and advanced querying capabilities.

## Table of Contents

1. [Send/Return Configuration](#sendreturn-configuration)
2. [Plugin Control](#plugin-control)
3. [Bus Operations](#bus-operations)
4. [Query Methods](#query-methods)
5. [Complete Workflows](#complete-workflows)

---

## Send/Return Configuration

Sends allow you to route audio from tracks to buses for effects processing, monitoring, or parallel processing.

### Set Send Level

Control the gain of a send on a track:

```python
# Set send 0 on track 1 to -12dB (typical reverb send level)
result = await set_send_level(track_id=1, send_id=0, level_db=-12.0)
# Returns: {'success': True, 'track_id': 1, 'send_id': 0, 'level_db': -12.0, ...}

# Set send 1 on track 2 to -6dB (less reverb)
result = await set_send_level(track_id=2, send_id=1, level_db=-6.0)

# Mute a send by setting to minimum level
result = await set_send_level(track_id=1, send_id=0, level_db=-193.0)
```

**Valid Range:** -193.0 dB (silent) to +6.0 dB (maximum boost)

### Enable/Disable Send

Toggle send processing on or off:

```python
# Enable send 0 on track 1
result = await enable_send(track_id=1, send_id=0, enabled=True)
# Returns: {'success': True, 'enabled': True, 'message': 'Enabled send 0 on track Vocals'}

# Disable send 1 on track 2
result = await enable_send(track_id=2, send_id=1, enabled=False)
# Returns: {'success': True, 'enabled': False, 'message': 'Disabled send 1 on track Guitar'}
```

### Toggle Send

Quickly toggle send state:

```python
# Toggle send 0 on track 1 (defaults to enabling if state unknown)
result = await toggle_send(track_id=1, send_id=0)
# Returns: {'success': True, 'enabled': True, ...}
```

### List Sends

Query all sends configured for a track:

```python
# List all sends on track 1
result = await list_sends(track_id=1)
# Returns: {'success': True, 'track_id': 1, 'send_count': 0, 'sends': [], ...}
```

**Note:** Send data caching is limited in the current implementation. For detailed send information, refer to the Ardour UI.

---

## Plugin Control

Control plugins (effects, instruments, processors) on tracks.

### Set Plugin Parameter

Adjust individual plugin parameters:

```python
# Set parameter 2 on plugin 0 (first plugin) of track 1 to 0.5
# Common use: Adjusting effect parameters like reverb decay, delay time, etc.
result = await set_plugin_parameter(
    track_id=1,
    plugin_id=0,
    param_id=2,
    value=0.5
)
# Returns: {'success': True, 'track_id': 1, 'plugin_id': 0, 'param_id': 2, 'value': 0.5}

# Set EQ frequency (parameter 0) on second plugin (plugin_id=1)
result = await set_plugin_parameter(
    track_id=1,
    plugin_id=1,
    param_id=0,
    value=0.75  # Value range is typically 0.0-1.0, mapped to plugin's actual range
)
```

**Parameter Values:** Typically normalized to 0.0-1.0, but plugin-dependent.

### Activate Plugin

Enable plugin processing:

```python
# Activate plugin 0 on track 1 (first plugin in chain)
result = await activate_plugin(track_id=1, plugin_id=0)
# Returns: {'success': True, 'plugin_id': 0, 'active': True, 'message': 'Activated plugin 0 on track Vocals'}

# Activate reverb plugin (second in chain)
result = await activate_plugin(track_id=1, plugin_id=1)
```

### Deactivate Plugin

Bypass plugin processing:

```python
# Deactivate (bypass) plugin 0 on track 1
result = await deactivate_plugin(track_id=1, plugin_id=0)
# Returns: {'success': True, 'plugin_id': 0, 'active': False, 'message': 'Deactivated plugin 0 on track Vocals'}

# Bypass EQ temporarily during recording
result = await deactivate_plugin(track_id=2, plugin_id=0)
```

### Toggle Plugin

Quickly toggle plugin active state:

```python
# Toggle plugin 0 on track 1 (defaults to activating if state unknown)
result = await toggle_plugin(track_id=1, plugin_id=0)
# Returns: {'success': True, 'plugin_id': 0, 'active': True, ...}
```

### Get Plugin Info

Query plugin information:

```python
# Get information about plugin 0 on track 1
result = await get_plugin_info(track_id=1, plugin_id=0)
# Returns: {'success': True, 'plugin_id': 0, 'name': '', 'active': None, 'param_count': 0, ...}
```

**Note:** Plugin details are not fully cached. Use Ardour UI for complete plugin information.

---

## Bus Operations

Buses are specialized tracks used for grouping, effects processing, or routing.

### List Buses

Get all buses in the session:

```python
# List all buses
result = await list_buses()
# Returns: {'success': True, 'bus_count': 0, 'buses': [], ...}
```

**Note:** Ardour's OSC has limited bus-specific query capabilities. Buses appear as tracks in the current implementation.

### Get Bus Info

Query information about a specific bus:

```python
# Get info for bus with strip ID 10
result = await get_bus_info(bus_id=10)
# Returns: {'success': True, 'bus_id': 10, 'name': 'Reverb Bus', 'gain_db': -12.0, ...}
```

### List Bus Sends

Find which tracks are sending to a bus:

```python
# List all sends going to bus 10 (e.g., reverb bus)
result = await list_bus_sends(bus_id=10)
# Returns: {'success': True, 'bus_id': 10, 'bus_name': 'Reverb Bus', 'send_count': 0, ...}
```

**Note:** Reverse send lookup is limited in Ardour's OSC implementation.

---

## Query Methods

Query cached state information without sending OSC commands.

### Get Send Level

Query send level from cache:

```python
# Query send 0 level on track 1
result = await get_send_level(track_id=1, send_id=0)
# Returns: {'success': True, 'send_id': 0, 'level_db': None, ...}
```

### Get Plugin Parameters

List all parameters for a plugin:

```python
# Get parameters for plugin 0 on track 1
result = await get_plugin_parameters(track_id=1, plugin_id=0)
# Returns: {'success': True, 'plugin_id': 0, 'param_count': 0, 'parameters': [], ...}
```

### Get Track Sends Count

Query how many sends are configured for a track:

```python
# Get send count for track 1
result = await get_track_sends_count(track_id=1)
# Returns: {'success': True, 'track_id': 1, 'send_count': 0, ...}
```

---

## Complete Workflows

### Example 1: Reverb Bus Setup

Set up a reverb bus with sends from multiple tracks:

```python
# Assume bus 10 is the reverb bus

# Set up send from vocals (track 1) to reverb bus
await set_send_level(track_id=1, send_id=0, level_db=-12.0)
await enable_send(track_id=1, send_id=0, enabled=True)

# Set up send from guitar (track 2) to reverb bus
await set_send_level(track_id=2, send_id=0, level_db=-18.0)
await enable_send(track_id=2, send_id=0, enabled=True)

# Set up send from bass (track 3) with less reverb
await set_send_level(track_id=3, send_id=0, level_db=-24.0)
await enable_send(track_id=3, send_id=0, enabled=True)

# Query the bus to verify
bus_info = await get_bus_info(bus_id=10)
print(f"Reverb bus '{bus_info['name']}' at {bus_info['gain_db']}dB")
```

### Example 2: Plugin Chain Management

Set up and control a plugin chain on a vocal track:

```python
# Track 1 = Vocals
# Plugin 0 = EQ
# Plugin 1 = Compressor
# Plugin 2 = De-esser

# Activate all plugins
await activate_plugin(track_id=1, plugin_id=0)  # EQ
await activate_plugin(track_id=1, plugin_id=1)  # Compressor
await activate_plugin(track_id=1, plugin_id=2)  # De-esser

# Set EQ parameters (example: boost high-mids)
await set_plugin_parameter(track_id=1, plugin_id=0, param_id=0, value=0.6)  # Frequency
await set_plugin_parameter(track_id=1, plugin_id=0, param_id=1, value=0.7)  # Gain

# Set compressor parameters
await set_plugin_parameter(track_id=1, plugin_id=1, param_id=0, value=0.4)  # Threshold
await set_plugin_parameter(track_id=1, plugin_id=1, param_id=1, value=0.6)  # Ratio

# Temporarily bypass de-esser during soft passages
await deactivate_plugin(track_id=1, plugin_id=2)

# Re-enable for bright sections
await activate_plugin(track_id=1, plugin_id=2)
```

### Example 3: Parallel Compression Setup

Create a parallel compression bus:

```python
# Assume bus 11 is the parallel compression bus

# Set up send from drums (track 4) to parallel compression bus
await set_send_level(track_id=4, send_id=0, level_db=-6.0)  # Hot send level
await enable_send(track_id=4, send_id=0, enabled=True)

# Activate aggressive compressor on the bus (assuming bus 11 has a compressor as plugin 0)
await activate_plugin(track_id=11, plugin_id=0)

# Set compressor to aggressive settings
await set_plugin_parameter(track_id=11, plugin_id=0, param_id=0, value=0.2)  # Low threshold
await set_plugin_parameter(track_id=11, plugin_id=0, param_id=1, value=0.9)  # High ratio

# Blend compressed signal back (adjust bus level)
await set_track_volume(track_id=11, volume_db=-18.0)  # Mix to taste
```

### Example 4: A/B Testing Effects

Quickly compare plugin settings:

```python
# Save current plugin state, then test new settings

# Bypass plugin to hear dry signal
await deactivate_plugin(track_id=1, plugin_id=0)
# Listen...

# Re-enable to hear wet signal
await activate_plugin(track_id=1, plugin_id=0)
# Listen...

# Try different parameter values
await set_plugin_parameter(track_id=1, plugin_id=0, param_id=2, value=0.3)
# Listen...

await set_plugin_parameter(track_id=1, plugin_id=0, param_id=2, value=0.7)
# Listen and compare...
```

### Example 5: Batch Send Configuration

Configure sends for multiple tracks at once:

```python
# Set up reverb sends for all vocal tracks
vocal_tracks = [1, 2, 3]  # Lead vocals, harmony 1, harmony 2

for track_id in vocal_tracks:
    # Set send level based on track importance
    if track_id == 1:  # Lead vocal
        level = -12.0
    else:  # Harmonies
        level = -18.0

    await set_send_level(track_id=track_id, send_id=0, level_db=level)
    await enable_send(track_id=track_id, send_id=0, enabled=True)
    print(f"Configured send for track {track_id} at {level}dB")
```

---

## OSC Commands Reference

### Send Commands
- `/strip/send/gain iif` - Set send gain (track_id, send_id, gain_db)
- `/strip/send/enable iii` - Enable/disable send (track_id, send_id, enable)

### Plugin Commands
- `/strip/plugin/parameter iiif` - Set parameter (track_id, plugin_id, param_id, value)
- `/strip/plugin/activate iii` - Activate/deactivate (track_id, plugin_id, activate)

---

## Implementation Notes

### Current Limitations

1. **Send Data Caching**: Send levels and routing information are not currently cached in the state system. Query methods return placeholder data.

2. **Plugin Information**: Plugin names, parameter names, and counts are not cached. Use Ardour UI for detailed plugin inspection.

3. **Bus Detection**: The current implementation does not distinguish buses from tracks in the state cache. Buses can be accessed using their strip IDs.

4. **OSC Feedback**: Ardour's OSC has limited feedback for sends and plugins. Some state changes may not trigger automatic cache updates.

### Future Enhancements

Potential improvements for future versions:

- Extended state caching for send levels and routing
- Plugin name and parameter metadata caching
- Bus type detection and filtering
- Bidirectional send routing queries
- Plugin preset management
- Extended parameter range handling

---

## Error Handling

All methods include comprehensive error handling:

```python
# Connection errors
result = await set_send_level(1, 0, -12.0)
if not result['success']:
    print(f"Error: {result['error']}")
    # Output: "Not connected to Ardour"

# Invalid track ID
result = await enable_send(track_id=999, send_id=0, enabled=True)
if not result['success']:
    print(f"Error: {result['error']}")
    # Output: "Track 999 not found"

# Out of range values
result = await set_send_level(track_id=1, send_id=0, level_db=10.0)
if not result['success']:
    print(f"Error: {result['error']}")
    # Output: "Send level 10.0dB out of range (-193.0 to +6.0)"

# Invalid IDs
result = await set_plugin_parameter(track_id=1, plugin_id=-1, param_id=0, value=0.5)
if not result['success']:
    print(f"Error: {result['error']}")
    # Output: "Plugin ID -1 invalid (must be >= 0)"
```

---

## Tips and Best Practices

### Send Levels
- **Reverb sends**: Start around -12dB to -18dB
- **Delay sends**: Start around -18dB to -24dB
- **Parallel compression**: Use hotter levels (-6dB to -12dB)
- **Monitor sends**: Adjust based on monitoring needs

### Plugin Management
- **CPU Management**: Deactivate unused plugins to save CPU
- **Signal Flow**: Order matters - EQ before compression is typical
- **A/B Comparison**: Use toggle functions for quick comparisons
- **Automation**: Consider automating plugin bypass for dynamic mixes

### Bus Routing
- **Effect Buses**: Use separate buses for each effect type
- **Subgroup Buses**: Group similar tracks (e.g., all drums)
- **Master Bus**: Keep master bus processing minimal and transparent

---

## Related Documentation

- [Basic Mixer Usage](README.md#mixer-control) - Volume, pan, mute, solo
- [Transport Control](README.md#transport-control) - Playback and recording
- [Track Management](README.md#track-management) - Creating and managing tracks

For the complete API reference, see the inline documentation in:
- `src/ardour_mcp/tools/advanced_mixer.py`
- `src/ardour_mcp/server.py`
