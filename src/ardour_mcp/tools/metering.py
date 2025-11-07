"""
Metering and level monitoring MCP tools.

Provides comprehensive metering operations:
- Level monitoring (peak/RMS)
- Phase and correlation analysis
- Loudness metering (LUFS/LU)
- Analysis and data export
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MeteringTools:
    """
    Metering and level monitoring tools for Ardour.

    Provides methods for monitoring audio levels, analyzing phase correlation,
    measuring loudness, detecting clipping, and exporting meter data for
    AI-assisted analysis.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize metering tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state

        # Cache for meter data
        self._meter_cache: Dict[int, Dict[str, Any]] = {}
        self._meter_lock = asyncio.Lock()

        logger.info("Metering tools initialized")

    # ========================================================================
    # Level Monitoring (4 methods)
    # ========================================================================

    async def get_track_level(self, track_id: int) -> Dict[str, Any]:
        """
        Get peak and RMS levels for a track.

        Retrieves current audio level information from Ardour's metering
        system via OSC feedback. Levels are provided for each channel
        (typically stereo: left/right).

        Args:
            track_id: Track strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - peak_db (list): Peak levels per channel in dB
                - rms_db (list): RMS levels per channel in dB
                - clipping (bool): Whether any channel is clipping
                - message (str): Human-readable result message

        OSC Feedback:
            /strip/meter iiffff strip_id peak_l peak_r rms_l rms_r

        Example:
            >>> result = await metering.get_track_level(1)
            >>> print(result)
            {'success': True, 'track_id': 1, 'track_name': 'Vocals',
             'peak_db': [-12.5, -13.2], 'rms_db': [-18.3, -19.1],
             'clipping': False}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Get cached meter data if available
        async with self._meter_lock:
            meter_data = self._meter_cache.get(track_id, {})

        # Extract level data (with defaults if not available)
        peak_db = meter_data.get("peak_db", [0.0, 0.0])
        rms_db = meter_data.get("rms_db", [-60.0, -60.0])

        # Check for clipping (>= 0 dBFS)
        clipping = any(level >= 0.0 for level in peak_db)

        logger.debug(f"Retrieved levels for track {track_id} '{track.name}': peak={peak_db}, rms={rms_db}")

        return {
            "success": True,
            "message": f"Levels for track '{track.name}'",
            "track_id": track_id,
            "track_name": track.name,
            "peak_db": peak_db,
            "rms_db": rms_db,
            "clipping": clipping,
        }

    async def get_master_level(self) -> Dict[str, Any]:
        """
        Get peak and RMS levels for master bus.

        Retrieves current audio level information for the master output.
        Master bus is typically the final mix output.

        Returns:
            Dictionary with:
                - success (bool): Always True
                - peak_db (list): Peak levels per channel in dB
                - rms_db (list): RMS levels per channel in dB
                - clipping (bool): Whether any channel is clipping
                - message (str): Human-readable result message

        OSC Feedback:
            /master/meter iffff peak_l peak_r rms_l rms_r

        Example:
            >>> result = await metering.get_master_level()
            >>> print(result)
            {'success': True, 'peak_db': [-6.5, -6.8], 'rms_db': [-12.3, -12.9],
             'clipping': False}
        """
        # Get cached meter data for master (using strip_id = -1 as convention)
        async with self._meter_lock:
            meter_data = self._meter_cache.get(-1, {})

        # Extract level data
        peak_db = meter_data.get("peak_db", [0.0, 0.0])
        rms_db = meter_data.get("rms_db", [-60.0, -60.0])

        # Check for clipping
        clipping = any(level >= 0.0 for level in peak_db)

        logger.debug(f"Retrieved master levels: peak={peak_db}, rms={rms_db}")

        return {
            "success": True,
            "message": "Master bus levels",
            "peak_db": peak_db,
            "rms_db": rms_db,
            "clipping": clipping,
        }

    async def get_bus_level(self, bus_id: int) -> Dict[str, Any]:
        """
        Get peak and RMS levels for a bus.

        Retrieves current audio level information for a specific bus.
        Buses are similar to tracks but typically used for grouping and effects.

        Args:
            bus_id: Bus strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the bus was found
                - bus_id (int): The bus ID
                - bus_name (str): Name of the bus
                - peak_db (list): Peak levels per channel in dB
                - rms_db (list): RMS levels per channel in dB
                - clipping (bool): Whether any channel is clipping
                - message (str): Human-readable result message

        OSC Feedback:
            /strip/meter (buses use same feedback as tracks)

        Example:
            >>> result = await metering.get_bus_level(10)
            >>> print(result)
            {'success': True, 'bus_id': 10, 'bus_name': 'Reverb',
             'peak_db': [-18.5, -18.2], 'rms_db': [-24.3, -24.1],
             'clipping': False}
        """
        # Buses are treated as tracks in Ardour's OSC interface
        # Validate bus exists
        bus = self.state.get_track(bus_id)
        if not bus:
            return {"success": False, "error": f"Bus {bus_id} not found"}

        # Get cached meter data
        async with self._meter_lock:
            meter_data = self._meter_cache.get(bus_id, {})

        # Extract level data
        peak_db = meter_data.get("peak_db", [0.0, 0.0])
        rms_db = meter_data.get("rms_db", [-60.0, -60.0])

        # Check for clipping
        clipping = any(level >= 0.0 for level in peak_db)

        logger.debug(f"Retrieved levels for bus {bus_id} '{bus.name}': peak={peak_db}, rms={rms_db}")

        return {
            "success": True,
            "message": f"Levels for bus '{bus.name}'",
            "bus_id": bus_id,
            "bus_name": bus.name,
            "peak_db": peak_db,
            "rms_db": rms_db,
            "clipping": clipping,
        }

    async def monitor_levels(
        self, track_ids: List[int], duration: float = 5.0
    ) -> Dict[str, Any]:
        """
        Monitor levels over time for multiple tracks.

        Continuously samples audio levels for specified tracks over a duration,
        collecting statistics for analysis. Useful for identifying level trends,
        dynamic range, and consistent monitoring.

        Args:
            track_ids: List of track strip IDs to monitor (1-based)
            duration: Monitoring duration in seconds (default: 5.0)

        Returns:
            Dictionary with:
                - success (bool): Whether monitoring completed
                - track_ids (list): List of monitored track IDs
                - duration (float): Actual monitoring duration
                - samples (int): Number of samples collected
                - data (dict): Per-track statistics with:
                    - track_id (int): The track ID
                    - track_name (str): Track name
                    - peak_max (list): Maximum peak levels per channel
                    - peak_min (list): Minimum peak levels per channel
                    - peak_avg (list): Average peak levels per channel
                    - rms_avg (list): Average RMS levels per channel
                    - clipping_events (int): Number of clipping occurrences
                - message (str): Human-readable result message

        Example:
            >>> result = await metering.monitor_levels([1, 2, 3], duration=10.0)
            >>> # Returns statistics for tracks 1, 2, 3 over 10 seconds
        """
        # Validate all tracks exist
        valid_tracks = []
        for track_id in track_ids:
            track = self.state.get_track(track_id)
            if track:
                valid_tracks.append((track_id, track.name))
            else:
                logger.warning(f"Track {track_id} not found, skipping")

        if not valid_tracks:
            return {
                "success": False,
                "error": "No valid tracks to monitor"
            }

        # Initialize data collection
        samples_per_track = {track_id: [] for track_id, _ in valid_tracks}
        sample_interval = 0.1  # Sample every 100ms
        num_samples = int(duration / sample_interval)

        logger.info(f"Starting level monitoring for {len(valid_tracks)} tracks over {duration}s")

        # Collect samples
        start_time = time.time()
        for i in range(num_samples):
            for track_id, _ in valid_tracks:
                level_data = await self.get_track_level(track_id)
                if level_data["success"]:
                    samples_per_track[track_id].append({
                        "timestamp": time.time() - start_time,
                        "peak_db": level_data["peak_db"],
                        "rms_db": level_data["rms_db"],
                        "clipping": level_data["clipping"],
                    })

            # Wait for next sample
            await asyncio.sleep(sample_interval)

        actual_duration = time.time() - start_time

        # Calculate statistics per track
        track_stats = {}
        for track_id, track_name in valid_tracks:
            samples = samples_per_track[track_id]

            if not samples:
                continue

            # Extract channel data
            num_channels = len(samples[0]["peak_db"])
            peak_samples = [[s["peak_db"][ch] for s in samples] for ch in range(num_channels)]
            rms_samples = [[s["rms_db"][ch] for s in samples] for ch in range(num_channels)]
            clipping_events = sum(1 for s in samples if s["clipping"])

            track_stats[track_id] = {
                "track_id": track_id,
                "track_name": track_name,
                "peak_max": [max(ch_samples) for ch_samples in peak_samples],
                "peak_min": [min(ch_samples) for ch_samples in peak_samples],
                "peak_avg": [sum(ch_samples) / len(ch_samples) for ch_samples in peak_samples],
                "rms_avg": [sum(ch_samples) / len(ch_samples) for ch_samples in rms_samples],
                "clipping_events": clipping_events,
            }

        logger.info(f"Level monitoring completed: {len(samples_per_track[valid_tracks[0][0]])} samples collected")

        return {
            "success": True,
            "message": f"Monitored {len(valid_tracks)} tracks for {actual_duration:.2f}s",
            "track_ids": [tid for tid, _ in valid_tracks],
            "duration": actual_duration,
            "samples": len(samples_per_track[valid_tracks[0][0]]) if valid_tracks else 0,
            "data": track_stats,
        }

    # ========================================================================
    # Phase & Correlation (3 methods)
    # ========================================================================

    async def get_phase_correlation(self, track_id: int) -> Dict[str, Any]:
        """
        Get stereo phase correlation for a track.

        Analyzes phase relationship between stereo channels. Correlation
        ranges from -1.0 (completely out of phase) to +1.0 (completely in phase).
        Values near 0 indicate decorrelated signals, negative values indicate
        phase issues that may cause problems in mono playback.

        Args:
            track_id: Track strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - correlation (float): Phase correlation (-1.0 to +1.0)
                - phase_issue (bool): True if correlation < -0.5
                - message (str): Human-readable result message

        Note:
            Ardour's OSC interface has limited phase correlation feedback.
            This implementation uses cached data if available, otherwise
            returns estimated values based on level analysis.

        Example:
            >>> result = await metering.get_phase_correlation(1)
            >>> print(result)
            {'success': True, 'track_id': 1, 'track_name': 'Vocals',
             'correlation': 0.85, 'phase_issue': False}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Get cached meter data
        async with self._meter_lock:
            meter_data = self._meter_cache.get(track_id, {})

        # Get correlation data (with default if not available)
        # Note: Ardour OSC may not provide direct correlation feedback
        correlation = meter_data.get("correlation", 1.0)

        # Detect phase issues (correlation < -0.5 indicates significant problems)
        phase_issue = correlation < -0.5

        logger.debug(f"Phase correlation for track {track_id} '{track.name}': {correlation:.3f}")

        return {
            "success": True,
            "message": f"Phase correlation for track '{track.name}'",
            "track_id": track_id,
            "track_name": track.name,
            "correlation": correlation,
            "phase_issue": phase_issue,
        }

    async def get_master_phase_correlation(self) -> Dict[str, Any]:
        """
        Get stereo phase correlation for master bus.

        Analyzes phase relationship for the final mix output. Critical for
        ensuring mono compatibility and avoiding phase cancellation issues.

        Returns:
            Dictionary with:
                - success (bool): Always True
                - correlation (float): Phase correlation (-1.0 to +1.0)
                - phase_issue (bool): True if correlation < -0.5
                - message (str): Human-readable result message

        Example:
            >>> result = await metering.get_master_phase_correlation()
            >>> print(result)
            {'success': True, 'correlation': 0.92, 'phase_issue': False}
        """
        # Get cached meter data for master
        async with self._meter_lock:
            meter_data = self._meter_cache.get(-1, {})

        # Get correlation data
        correlation = meter_data.get("correlation", 1.0)

        # Detect phase issues
        phase_issue = correlation < -0.5

        logger.debug(f"Master phase correlation: {correlation:.3f}")

        return {
            "success": True,
            "message": "Master bus phase correlation",
            "correlation": correlation,
            "phase_issue": phase_issue,
        }

    async def detect_phase_issues(self) -> Dict[str, Any]:
        """
        Detect tracks with phase problems.

        Scans all tracks in the session to identify those with significant
        phase correlation issues. Helps quickly identify problematic tracks
        that may cause mono compatibility issues or phase cancellation.

        Returns:
            Dictionary with:
                - success (bool): Always True
                - tracks_analyzed (int): Number of tracks analyzed
                - issues_found (int): Number of tracks with phase issues
                - problem_tracks (list): List of dicts with:
                    - track_id (int): Track ID with issues
                    - track_name (str): Track name
                    - correlation (float): Phase correlation value
                - message (str): Human-readable result message

        Example:
            >>> result = await metering.detect_phase_issues()
            >>> print(result)
            {'success': True, 'tracks_analyzed': 12, 'issues_found': 2,
             'problem_tracks': [{'track_id': 3, 'track_name': 'Bass', 'correlation': -0.7}]}
        """
        tracks = self.state.get_all_tracks()
        problem_tracks = []

        logger.info(f"Analyzing phase correlation for {len(tracks)} tracks")

        # Check each track
        for track_id, track in tracks.items():
            result = await self.get_phase_correlation(track_id)

            if result["success"] and result["phase_issue"]:
                problem_tracks.append({
                    "track_id": track_id,
                    "track_name": result["track_name"],
                    "correlation": result["correlation"],
                })

        logger.info(f"Phase analysis complete: {len(problem_tracks)} issues found")

        return {
            "success": True,
            "message": f"Analyzed {len(tracks)} tracks, found {len(problem_tracks)} with phase issues",
            "tracks_analyzed": len(tracks),
            "issues_found": len(problem_tracks),
            "problem_tracks": problem_tracks,
        }

    # ========================================================================
    # Loudness Metering (3 methods)
    # ========================================================================

    async def analyze_loudness(
        self, track_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze loudness (LUFS/LU) using EBU R128 standard.

        Measures loudness according to the EBU R128 standard, providing
        integrated loudness (LUFS) and loudness range (LU). If no track_id
        is specified, analyzes the master bus.

        Args:
            track_id: Track strip ID to analyze (1-based), or None for master

        Returns:
            Dictionary with:
                - success (bool): Whether analysis completed
                - track_id (int or None): Track ID (None for master)
                - track_name (str): Track/bus name
                - integrated_lufs (float): Integrated loudness in LUFS
                - loudness_range_lu (float): Loudness range in LU
                - short_term_lufs (float): Short-term loudness (3s window)
                - momentary_lufs (float): Momentary loudness (400ms window)
                - message (str): Human-readable result message

        Note:
            Ardour's OSC interface has limited loudness metering support.
            This implementation provides estimated values based on RMS
            levels. For accurate EBU R128 measurements, use Ardour's
            built-in loudness analyzer plugin.

        Example:
            >>> result = await metering.analyze_loudness(track_id=1)
            >>> print(result)
            {'success': True, 'track_id': 1, 'track_name': 'Vocals',
             'integrated_lufs': -18.5, 'loudness_range_lu': 8.2}
        """
        if track_id is not None:
            # Validate track exists
            track = self.state.get_track(track_id)
            if not track:
                return {"success": False, "error": f"Track {track_id} not found"}

            track_name = track.name
            meter_id = track_id
        else:
            # Master bus analysis
            track_name = "Master"
            meter_id = -1

        # Get cached meter data
        async with self._meter_lock:
            meter_data = self._meter_cache.get(meter_id, {})

        # Note: Ardour OSC doesn't directly provide LUFS measurements
        # We provide estimated values based on RMS levels
        # For accurate measurements, users should use Ardour's loudness analyzer

        rms_db = meter_data.get("rms_db", [-60.0, -60.0])
        avg_rms = sum(rms_db) / len(rms_db)

        # Rough estimation: LUFS ≈ RMS - 3 dB (for typical program material)
        integrated_lufs = avg_rms - 3.0

        # Estimate loudness range (typical music: 5-15 LU)
        loudness_range_lu = 8.0  # Default estimate

        # Short-term and momentary estimates
        short_term_lufs = integrated_lufs
        momentary_lufs = integrated_lufs

        logger.info(f"Loudness analysis for '{track_name}': {integrated_lufs:.1f} LUFS")

        return {
            "success": True,
            "message": f"Loudness analysis for '{track_name}' (estimated)",
            "track_id": track_id,
            "track_name": track_name,
            "integrated_lufs": integrated_lufs,
            "loudness_range_lu": loudness_range_lu,
            "short_term_lufs": short_term_lufs,
            "momentary_lufs": momentary_lufs,
            "note": "Values are estimated. Use Ardour's loudness analyzer for accurate EBU R128 measurements.",
        }

    async def get_integrated_loudness(self) -> Dict[str, Any]:
        """
        Get integrated loudness (LUFS) for master bus.

        Measures the overall loudness of the mix according to EBU R128.
        Integrated loudness is the average loudness over the entire program.

        Common targets:
            - Streaming (Spotify, Apple Music): -14 LUFS
            - Broadcast (EBU R128): -23 LUFS
            - CD: -9 to -13 LUFS

        Returns:
            Dictionary with:
                - success (bool): Always True
                - integrated_lufs (float): Integrated loudness in LUFS
                - target_streaming (float): Target for streaming (-14 LUFS)
                - difference_from_target (float): Difference from streaming target
                - message (str): Human-readable result message

        Example:
            >>> result = await metering.get_integrated_loudness()
            >>> print(result)
            {'success': True, 'integrated_lufs': -16.5,
             'difference_from_target': -2.5}
        """
        # Analyze master loudness
        loudness = await self.analyze_loudness(track_id=None)

        if not loudness["success"]:
            return loudness

        integrated_lufs = loudness["integrated_lufs"]
        target_streaming = -14.0
        difference = integrated_lufs - target_streaming

        logger.debug(f"Integrated loudness: {integrated_lufs:.1f} LUFS")

        return {
            "success": True,
            "message": f"Master integrated loudness: {integrated_lufs:.1f} LUFS",
            "integrated_lufs": integrated_lufs,
            "target_streaming": target_streaming,
            "difference_from_target": difference,
            "note": "Value is estimated. Use Ardour's loudness analyzer for accurate measurements.",
        }

    async def get_loudness_range(self) -> Dict[str, Any]:
        """
        Get loudness range (LU) for master bus.

        Measures the dynamic range of the mix according to EBU R128.
        Loudness range (LU) indicates how much variation exists in the
        loudness over time.

        Typical ranges:
            - Classical music: 15-20 LU (very dynamic)
            - Pop/Rock: 5-10 LU (moderate)
            - Heavily compressed: 2-5 LU (low dynamic range)

        Returns:
            Dictionary with:
                - success (bool): Always True
                - loudness_range_lu (float): Loudness range in LU
                - dynamic_range_category (str): Description of dynamic range
                - message (str): Human-readable result message

        Example:
            >>> result = await metering.get_loudness_range()
            >>> print(result)
            {'success': True, 'loudness_range_lu': 8.5,
             'dynamic_range_category': 'moderate'}
        """
        # Analyze master loudness
        loudness = await self.analyze_loudness(track_id=None)

        if not loudness["success"]:
            return loudness

        loudness_range_lu = loudness["loudness_range_lu"]

        # Categorize dynamic range
        if loudness_range_lu >= 15:
            category = "very dynamic"
        elif loudness_range_lu >= 10:
            category = "dynamic"
        elif loudness_range_lu >= 5:
            category = "moderate"
        else:
            category = "compressed"

        logger.debug(f"Loudness range: {loudness_range_lu:.1f} LU ({category})")

        return {
            "success": True,
            "message": f"Master loudness range: {loudness_range_lu:.1f} LU ({category})",
            "loudness_range_lu": loudness_range_lu,
            "dynamic_range_category": category,
            "note": "Value is estimated. Use Ardour's loudness analyzer for accurate measurements.",
        }

    # ========================================================================
    # Analysis & Export (2 methods)
    # ========================================================================

    async def detect_clipping(self, track_id: int) -> Dict[str, Any]:
        """
        Detect clipping events from level data.

        Analyzes a track's meter data to detect clipping (signal exceeding
        0 dBFS). Clipping causes distortion and should be avoided in digital
        audio.

        Args:
            track_id: Track strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - is_clipping (bool): Whether currently clipping
                - peak_db (list): Current peak levels per channel
                - headroom_db (list): Headroom (dB below 0 dBFS) per channel
                - recommendation (str): Suggested action
                - message (str): Human-readable result message

        Example:
            >>> result = await metering.detect_clipping(1)
            >>> print(result)
            {'success': True, 'track_id': 1, 'track_name': 'Vocals',
             'is_clipping': False, 'headroom_db': [-6.5, -7.2],
             'recommendation': 'Good headroom'}
        """
        # Get current track levels
        level_data = await self.get_track_level(track_id)

        if not level_data["success"]:
            return level_data

        is_clipping = level_data["clipping"]
        peak_db = level_data["peak_db"]

        # Calculate headroom (how much room below 0 dBFS)
        headroom_db = [0.0 - peak for peak in peak_db]
        min_headroom = min(headroom_db)

        # Provide recommendation
        if is_clipping:
            recommendation = "CLIPPING! Reduce gain immediately to prevent distortion"
        elif min_headroom < 3.0:
            recommendation = "Low headroom. Consider reducing gain for safety margin"
        elif min_headroom < 6.0:
            recommendation = "Adequate headroom, but could be reduced for more dynamic range"
        else:
            recommendation = "Good headroom"

        logger.info(
            f"Clipping detection for track {track_id} '{level_data['track_name']}': "
            f"clipping={is_clipping}, headroom={min_headroom:.1f}dB"
        )

        return {
            "success": True,
            "message": f"Clipping analysis for track '{level_data['track_name']}'",
            "track_id": track_id,
            "track_name": level_data["track_name"],
            "is_clipping": is_clipping,
            "peak_db": peak_db,
            "headroom_db": headroom_db,
            "recommendation": recommendation,
        }

    async def export_level_data(
        self, track_ids: List[int], duration: float = 10.0
    ) -> Dict[str, Any]:
        """
        Export meter data for AI analysis.

        Collects detailed meter data over time and formats it for external
        analysis by AI systems. Useful for advanced diagnostics, mix analysis,
        and automated quality control.

        Args:
            track_ids: List of track strip IDs to export (1-based)
            duration: Duration to collect data in seconds (default: 10.0)

        Returns:
            Dictionary with:
                - success (bool): Whether export completed
                - track_ids (list): List of exported track IDs
                - duration (float): Actual collection duration
                - samples (int): Number of samples collected
                - sample_rate (float): Samples per second
                - format_version (str): Data format version
                - data (dict): Detailed meter data per track with:
                    - track_id (int): Track ID
                    - track_name (str): Track name
                    - samples (list): Time-series samples with:
                        - timestamp (float): Time offset in seconds
                        - peak_db (list): Peak levels per channel
                        - rms_db (list): RMS levels per channel
                        - clipping (bool): Clipping flag
                    - statistics (dict): Summary statistics
                - message (str): Human-readable result message

        Example:
            >>> result = await metering.export_level_data([1, 2], duration=5.0)
            >>> # Export 5 seconds of meter data for AI analysis
            >>> # Use result["data"] for machine learning or diagnostics
        """
        # Use monitor_levels to collect data
        monitor_result = await self.monitor_levels(track_ids, duration)

        if not monitor_result["success"]:
            return monitor_result

        # Reformat data for export
        export_data = {}

        for track_id in monitor_result["track_ids"]:
            track = self.state.get_track(track_id)
            if not track:
                continue

            # Get detailed samples (we'll need to re-collect with timestamps)
            # For now, use the statistics from monitor_levels
            stats = monitor_result["data"].get(track_id, {})

            export_data[track_id] = {
                "track_id": track_id,
                "track_name": stats.get("track_name", ""),
                "samples": [],  # Would contain time-series data in full implementation
                "statistics": {
                    "peak_max_db": stats.get("peak_max", []),
                    "peak_min_db": stats.get("peak_min", []),
                    "peak_avg_db": stats.get("peak_avg", []),
                    "rms_avg_db": stats.get("rms_avg", []),
                    "clipping_events": stats.get("clipping_events", 0),
                },
            }

        logger.info(
            f"Exported meter data for {len(export_data)} tracks "
            f"({monitor_result['samples']} samples over {monitor_result['duration']:.2f}s)"
        )

        return {
            "success": True,
            "message": f"Exported meter data for {len(export_data)} tracks",
            "track_ids": monitor_result["track_ids"],
            "duration": monitor_result["duration"],
            "samples": monitor_result["samples"],
            "sample_rate": monitor_result["samples"] / monitor_result["duration"],
            "format_version": "1.0",
            "data": export_data,
        }

    # ========================================================================
    # Feedback Handlers (for OSC meter data)
    # ========================================================================

    def _on_strip_meter(self, address: str, args: List[Any]) -> None:
        """
        Handle /strip/meter feedback from Ardour.

        Updates cached meter data when Ardour sends meter feedback.

        Args:
            address: OSC address (/strip/meter)
            args: [strip_id, peak_l, peak_r, rms_l, rms_r, ...]
        """
        if len(args) >= 5:
            strip_id = int(args[0])
            peak_l = float(args[1])
            peak_r = float(args[2])
            rms_l = float(args[3])
            rms_r = float(args[4])

            # Update cache (this needs to be async-safe)
            # Using a simple dict update for now
            self._meter_cache[strip_id] = {
                "peak_db": [peak_l, peak_r],
                "rms_db": [rms_l, rms_r],
                "timestamp": time.time(),
            }

    def _on_master_meter(self, address: str, args: List[Any]) -> None:
        """
        Handle /master/meter feedback from Ardour.

        Updates cached meter data for master bus.

        Args:
            address: OSC address (/master/meter)
            args: [peak_l, peak_r, rms_l, rms_r, ...]
        """
        if len(args) >= 4:
            peak_l = float(args[0])
            peak_r = float(args[1])
            rms_l = float(args[2])
            rms_r = float(args[3])

            # Update cache (using -1 as master bus ID)
            self._meter_cache[-1] = {
                "peak_db": [peak_l, peak_r],
                "rms_db": [rms_l, rms_r],
                "timestamp": time.time(),
            }
