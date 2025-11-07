# Metering & Level Monitoring Usage Guide

This guide demonstrates how to use the Ardour MCP metering and level monitoring tools for comprehensive audio analysis.

## Overview

The metering tools provide:
- **Level Monitoring**: Track peak/RMS levels for individual tracks, buses, and master
- **Phase & Correlation**: Analyze stereo phase relationships and detect phase issues
- **Loudness Metering**: Measure integrated loudness (LUFS) and loudness range (LU) per EBU R128
- **Analysis & Export**: Detect clipping and export meter data for AI analysis

## Level Monitoring

### Get Track Level

Retrieve current peak and RMS levels for a specific track:

```python
result = await get_track_level(track_id=1)
# Returns:
# {
#     "success": True,
#     "track_id": 1,
#     "track_name": "Vocals",
#     "peak_db": [-12.5, -13.2],  # Left/right channels
#     "rms_db": [-18.3, -19.1],
#     "clipping": False
# }
```

### Get Master Level

Retrieve master bus levels:

```python
result = await get_master_level()
# Returns:
# {
#     "success": True,
#     "peak_db": [-6.5, -6.8],
#     "rms_db": [-12.3, -12.9],
#     "clipping": False
# }
```

### Get Bus Level

Monitor levels for a specific bus:

```python
result = await get_bus_level(bus_id=10)
# Returns:
# {
#     "success": True,
#     "bus_id": 10,
#     "bus_name": "Reverb",
#     "peak_db": [-18.5, -18.2],
#     "rms_db": [-24.3, -24.1],
#     "clipping": False
# }
```

### Monitor Levels Over Time

Continuously sample levels for multiple tracks:

```python
result = await monitor_levels(
    track_ids=[1, 2, 3],
    duration=10.0  # Monitor for 10 seconds
)
# Returns:
# {
#     "success": True,
#     "track_ids": [1, 2, 3],
#     "duration": 10.05,
#     "samples": 100,
#     "data": {
#         1: {
#             "track_id": 1,
#             "track_name": "Vocals",
#             "peak_max": [-8.0, -8.5],
#             "peak_min": [-15.0, -16.0],
#             "peak_avg": [-11.5, -12.3],
#             "rms_avg": [-17.8, -18.5],
#             "clipping_events": 0
#         },
#         # ... data for tracks 2 and 3
#     }
# }
```

**Use Cases:**
- Monitor levels during recording/mixing
- Identify dynamic range of tracks
- Detect problematic level variations
- Gather statistics for mix analysis

## Phase & Correlation Analysis

### Get Phase Correlation

Analyze stereo phase relationship for a track:

```python
result = await get_phase_correlation(track_id=1)
# Returns:
# {
#     "success": True,
#     "track_id": 1,
#     "track_name": "Vocals",
#     "correlation": 0.85,  # Range: -1.0 to +1.0
#     "phase_issue": False
# }
```

**Correlation Values:**
- `+1.0`: Perfectly in phase (mono signal)
- `0.0`: Completely decorrelated (wide stereo)
- `-1.0`: Completely out of phase (phase cancellation)
- `< -0.5`: Significant phase issue (mono compatibility problem)

### Get Master Phase Correlation

Check phase correlation for the master mix:

```python
result = await get_master_phase_correlation()
# Returns:
# {
#     "success": True,
#     "correlation": 0.92,
#     "phase_issue": False
# }
```

### Detect Phase Issues

Scan all tracks for phase problems:

```python
result = await detect_phase_issues()
# Returns:
# {
#     "success": True,
#     "tracks_analyzed": 12,
#     "issues_found": 2,
#     "problem_tracks": [
#         {
#             "track_id": 3,
#             "track_name": "Bass",
#             "correlation": -0.7
#         },
#         {
#             "track_id": 7,
#             "track_name": "Overhead L",
#             "correlation": -0.6
#         }
#     ]
# }
```

**Use Cases:**
- Check mono compatibility before mastering
- Identify mic positioning issues
- Detect polarity problems
- Quality control for stereo recordings

## Loudness Metering (EBU R128)

### Analyze Loudness

Measure loudness for a track or master:

```python
# Analyze specific track
result = await analyze_loudness(track_id=1)

# Analyze master bus
result = await analyze_loudness(track_id=None)

# Returns:
# {
#     "success": True,
#     "track_id": 1,
#     "track_name": "Vocals",
#     "integrated_lufs": -18.5,    # Overall loudness
#     "loudness_range_lu": 8.2,     # Dynamic range
#     "short_term_lufs": -17.8,     # 3-second window
#     "momentary_lufs": -16.5,      # 400ms window
#     "note": "Values are estimated..."
# }
```

**Note:** Ardour's OSC interface has limited loudness metering support. These values are estimated based on RMS levels. For accurate EBU R128 measurements, use Ardour's built-in loudness analyzer plugin.

### Get Integrated Loudness

Measure master integrated loudness with target comparison:

```python
result = await get_integrated_loudness()
# Returns:
# {
#     "success": True,
#     "integrated_lufs": -16.5,
#     "target_streaming": -14.0,
#     "difference_from_target": -2.5  # 2.5 dB quieter than target
# }
```

**Common Loudness Targets:**
- **Streaming (Spotify, Apple Music)**: -14 LUFS
- **Broadcast (EBU R128)**: -23 LUFS
- **CD**: -9 to -13 LUFS
- **YouTube**: -13 to -15 LUFS

### Get Loudness Range

Measure dynamic range of the mix:

```python
result = await get_loudness_range()
# Returns:
# {
#     "success": True,
#     "loudness_range_lu": 8.5,
#     "dynamic_range_category": "moderate"
# }
```

**Loudness Range Categories:**
- **Very Dynamic** (15-20 LU): Classical, jazz, acoustic
- **Dynamic** (10-15 LU): Rock, folk, singer-songwriter
- **Moderate** (5-10 LU): Pop, electronic, modern mixes
- **Compressed** (2-5 LU): Heavy pop, EDM, heavily mastered

**Use Cases:**
- Prepare masters for streaming platforms
- Ensure broadcast compliance
- Maintain competitive loudness levels
- Preserve dynamic range in mixes

## Clipping Detection & Analysis

### Detect Clipping

Check for clipping and analyze headroom:

```python
result = await detect_clipping(track_id=1)
# Returns:
# {
#     "success": True,
#     "track_id": 1,
#     "track_name": "Vocals",
#     "is_clipping": False,
#     "peak_db": [-6.5, -7.2],
#     "headroom_db": [6.5, 7.2],  # dB below 0 dBFS
#     "recommendation": "Good headroom"
# }
```

**Recommendations:**
- **Clipping** (peak >= 0 dB): "CLIPPING! Reduce gain immediately"
- **Low Headroom** (< 3 dB): "Low headroom. Consider reducing gain"
- **Adequate** (3-6 dB): "Adequate headroom, but could be reduced"
- **Good** (> 6 dB): "Good headroom"

**Best Practices:**
- Maintain 3-6 dB headroom during mixing
- Keep 6-10 dB headroom for stems and pre-master
- Peak at -1 dB or lower for final masters

## Data Export for AI Analysis

### Export Level Data

Collect detailed meter data for machine learning or advanced analysis:

```python
result = await export_level_data(
    track_ids=[1, 2, 3, 4],
    duration=30.0  # Collect 30 seconds of data
)
# Returns:
# {
#     "success": True,
#     "track_ids": [1, 2, 3, 4],
#     "duration": 30.12,
#     "samples": 301,
#     "sample_rate": 10.0,  # Samples per second
#     "format_version": "1.0",
#     "data": {
#         1: {
#             "track_id": 1,
#             "track_name": "Vocals",
#             "samples": [],  # Time-series data (full implementation)
#             "statistics": {
#                 "peak_max_db": [-8.0, -8.5],
#                 "peak_min_db": [-18.0, -19.0],
#                 "peak_avg_db": [-13.0, -13.8],
#                 "rms_avg_db": [-19.0, -19.7],
#                 "clipping_events": 0
#             }
#         },
#         # ... data for other tracks
#     }
# }
```

**Use Cases:**
- Train ML models for mix quality assessment
- Automated gain staging recommendations
- Pattern recognition in professional mixes
- Quality control automation
- Historical mixing analysis

## Complete Workflow Examples

### Pre-Mix Level Check

```python
# 1. Check master levels
master = await get_master_level()
if master["clipping"]:
    print("WARNING: Master is clipping!")

# 2. Check all tracks for clipping
tracks = [1, 2, 3, 4, 5]  # Your track IDs
for track_id in tracks:
    result = await detect_clipping(track_id)
    if result["is_clipping"]:
        print(f"Track {result['track_name']} is clipping!")
    elif min(result["headroom_db"]) < 3.0:
        print(f"Track {result['track_name']} has low headroom")

# 3. Check for phase issues
phase_check = await detect_phase_issues()
if phase_check["issues_found"] > 0:
    print(f"Found phase issues in {phase_check['issues_found']} tracks:")
    for track in phase_check["problem_tracks"]:
        print(f"  - {track['track_name']}: correlation {track['correlation']:.2f}")
```

### Pre-Master Quality Control

```python
# 1. Analyze master loudness
loudness = await get_integrated_loudness()
print(f"Integrated loudness: {loudness['integrated_lufs']:.1f} LUFS")
print(f"Difference from streaming target: {loudness['difference_from_target']:.1f} dB")

# 2. Check dynamic range
dr = await get_loudness_range()
print(f"Loudness range: {dr['loudness_range_lu']:.1f} LU ({dr['dynamic_range_category']})")

# 3. Verify master phase correlation
phase = await get_master_phase_correlation()
print(f"Master correlation: {phase['correlation']:.2f}")
if phase["phase_issue"]:
    print("WARNING: Master has phase issues - check mono compatibility!")

# 4. Final clipping check
master_clip = await detect_clipping(track_id=1)  # Replace with master track ID
print(f"Peak level: {max(master_clip['peak_db']):.1f} dB")
print(f"Headroom: {min(master_clip['headroom_db']):.1f} dB")
```

### Mix Monitoring Session

```python
# Monitor key tracks during a mix session
import asyncio

async def monitor_mix():
    # Track IDs for vocals, drums, bass, master
    track_ids = [1, 2, 3]

    while True:
        # Get current levels
        for track_id in track_ids:
            level = await get_track_level(track_id)
            print(f"{level['track_name']}: "
                  f"Peak L/R: {level['peak_db'][0]:.1f}/{level['peak_db'][1]:.1f} dB, "
                  f"RMS L/R: {level['rms_db'][0]:.1f}/{level['rms_db'][1]:.1f} dB")

        # Check master
        master = await get_master_level()
        print(f"Master: Peak L/R: {master['peak_db'][0]:.1f}/{master['peak_db'][1]:.1f} dB")
        print("-" * 60)

        await asyncio.sleep(1.0)  # Update every second

# Run monitoring
await monitor_mix()
```

## Tips & Best Practices

### Level Monitoring
1. **Headroom**: Maintain 3-6 dB headroom during mixing
2. **Peak vs RMS**: Use RMS for perceived loudness, peak for clipping detection
3. **Stereo Balance**: Watch for large L/R level differences (> 3 dB)
4. **Bus Levels**: Monitor reverb/delay buses to prevent feedback buildup

### Phase Correlation
1. **Mono Check**: Test mixes with correlation meter in mono
2. **Problem Sources**: Check drum overheads, stereo mics, doubled guitars
3. **Acceptable Range**: 0.3 to 1.0 is generally safe for most material
4. **Fixing Issues**: Try phase inversion, mic repositioning, or timing adjustment

### Loudness Metering
1. **Streaming**: Target -14 LUFS for most platforms
2. **Dynamic Range**: Preserve 7-12 LU for modern pop, 12-18 LU for acoustic
3. **Measurement Duration**: Analyze full mix, not just sections
4. **Reference**: Compare to professional releases in your genre

### Clipping Prevention
1. **Set Levels Early**: Establish proper gain staging from the start
2. **Watch Sum Buses**: Group/bus summing can cause unexpected clipping
3. **Plugin Headroom**: Some plugins need headroom to work properly
4. **True Peak**: Consider true peak limiting for final masters

## Troubleshooting

### No Meter Data Available
- Ensure Ardour is sending OSC feedback
- Check OSC configuration in Ardour preferences
- Verify network connection to Ardour OSC server
- Enable meter feedback in Ardour OSC settings

### Inaccurate Readings
- Meter cache may be stale - readings update with OSC feedback
- Ensure sufficient monitoring duration for accurate statistics
- Some values (LUFS) are estimated - use Ardour plugins for precision

### Performance Issues
- Reduce monitoring duration for faster results
- Monitor fewer tracks simultaneously
- Adjust sample interval in monitoring functions
- Consider exporting data for offline analysis

## Integration with Other Tools

### With Mixer Tools
```python
# Adjust levels based on metering
level = await get_track_level(track_id=1)
if max(level["peak_db"]) > -3.0:
    # Reduce gain by 3 dB
    await set_track_volume(track_id=1, volume_db=-3.0)
```

### With Transport Tools
```python
# Monitor levels during playback
await transport_play()
await asyncio.sleep(2.0)  # Let playback stabilize

# Collect 10 seconds of level data
data = await monitor_levels(track_ids=[1, 2, 3], duration=10.0)

await transport_stop()
```

### With Automation Tools
```python
# Check levels before recording automation
level = await get_track_level(track_id=1)
if not level["clipping"]:
    # Safe to record automation
    await enable_automation_write(track_id=1)
```

## API Reference Summary

### Level Monitoring (4 methods)
- `get_track_level(track_id: int)` - Get peak/RMS for track
- `get_master_level()` - Get peak/RMS for master
- `get_bus_level(bus_id: int)` - Get peak/RMS for bus
- `monitor_levels(track_ids: List[int], duration: float)` - Monitor over time

### Phase & Correlation (3 methods)
- `get_phase_correlation(track_id: int)` - Get track phase correlation
- `get_master_phase_correlation()` - Get master phase correlation
- `detect_phase_issues()` - Scan all tracks for phase problems

### Loudness Metering (3 methods)
- `analyze_loudness(track_id: Optional[int])` - Analyze LUFS/LU
- `get_integrated_loudness()` - Get master integrated LUFS
- `get_loudness_range()` - Get master loudness range

### Analysis & Export (2 methods)
- `detect_clipping(track_id: int)` - Detect clipping and check headroom
- `export_level_data(track_ids: List[int], duration: float)` - Export for AI analysis

---

For more information, see the main [README.md](README.md) and [API documentation](docs/API.md).
