"""
Recording control MCP tools.

Provides tools for recording operations:
- Global recording control (start, stop, toggle)
- Punch recording (punch-in/out ranges)
- Input/disk monitoring control
- Recording state queries
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class RecordingTools:
    """
    Recording control tools for Ardour.

    Provides methods for controlling recording operations including
    global recording control, punch recording, and input monitoring.

    Note: Track arming (arm_track_for_recording, disarm_track) is
    implemented in MixerTools to keep mixer-related operations together.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize recording tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state
        logger.info("Recording tools initialized")

    # =========================================================================
    # Global Recording Control
    # =========================================================================

    async def start_recording(self) -> Dict[str, Any]:
        """
        Start recording with automatic transport play.

        Enables global record mode and starts transport playback.
        Checks if already recording to avoid state conflicts.
        Will only record on tracks that are armed for recording.

        Returns:
            Dictionary with:
                - success (bool): Whether recording was started
                - recording (bool): Current recording state
                - armed_tracks (list): List of track IDs armed for recording
                - message (str): Human-readable result message

        OSC Commands:
            /rec_enable_toggle (if not already recording)
            /transport_play

        Example:
            >>> result = await recording.start_recording()
            >>> print(result)
            {'success': True, 'message': 'Recording started with 2 armed track(s)',
             'recording': True, 'armed_tracks': [1, 3]}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check if already recording
        transport = self.state.get_transport()
        if transport.recording:
            return {
                "success": False,
                "error": "Already recording",
                "recording": True,
            }

        # Get armed tracks before starting
        armed = [
            track.strip_id
            for track in self.state.get_all_tracks().values()
            if track.rec_enabled
        ]

        if len(armed) == 0:
            logger.warning("Starting recording with no armed tracks")

        # Enable recording
        rec_success = self.osc.send_command("/rec_enable_toggle")
        if not rec_success:
            return {"success": False, "error": "Failed to enable recording"}

        # Start transport
        play_success = self.osc.send_command("/transport_play")
        if not play_success:
            # Rollback recording enable
            self.osc.send_command("/rec_enable_toggle")
            return {"success": False, "error": "Failed to start transport"}

        logger.info(f"Recording started with {len(armed)} armed track(s)")
        return {
            "success": True,
            "message": f"Recording started with {len(armed)} armed track(s)",
            "recording": True,
            "armed_tracks": armed,
        }

    async def stop_recording(self) -> Dict[str, Any]:
        """
        Stop recording and transport.

        Stops transport and disables global record mode.
        Safe to call even if not currently recording.

        Returns:
            Dictionary with:
                - success (bool): Whether recording was stopped
                - recording (bool): Current recording state (False after stop)
                - message (str): Human-readable result message

        OSC Commands:
            /transport_stop
            /rec_enable_toggle (if recording was enabled)

        Example:
            >>> result = await recording.stop_recording()
            >>> print(result)
            {'success': True, 'message': 'Recording stopped', 'recording': False}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check if currently recording
        transport = self.state.get_transport()
        was_recording = transport.recording

        # Stop transport first
        stop_success = self.osc.send_command("/transport_stop")
        if not stop_success:
            return {"success": False, "error": "Failed to stop transport"}

        # Disable recording if it was enabled
        if was_recording:
            rec_success = self.osc.send_command("/rec_enable_toggle")
            if not rec_success:
                logger.warning("Failed to disable recording mode after stopping transport")
                return {
                    "success": False,
                    "error": "Transport stopped but failed to disable recording mode",
                }

        logger.info("Recording stopped")
        return {
            "success": True,
            "message": "Recording stopped",
            "recording": False,
        }

    async def toggle_recording(self) -> Dict[str, Any]:
        """
        Toggle global record enable state.

        Toggles the record enable button state. Does not affect transport.
        To start recording with playback, use start_recording() instead.

        Returns:
            Dictionary with:
                - success (bool): Whether recording state was toggled
                - recording (bool): New recording state
                - message (str): Human-readable result message

        OSC Commands:
            /rec_enable_toggle

        Example:
            >>> result = await recording.toggle_recording()
            >>> print(result)
            {'success': True, 'message': 'Record enable toggled', 'recording': True}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Toggle recording
        success = self.osc.send_command("/rec_enable_toggle")
        if not success:
            return {"success": False, "error": "Failed to toggle recording"}

        # Get new state (note: state might not be updated immediately)
        transport = self.state.get_transport()
        new_recording = not transport.recording

        logger.info(f"Record enable toggled to: {new_recording}")
        return {
            "success": True,
            "message": "Record enable toggled",
            "recording": new_recording,
        }

    async def is_recording(self) -> Dict[str, Any]:
        """
        Query current recording state from cache.

        Returns cached recording state without sending OSC commands.
        Provides information about recording status and armed tracks.

        Returns:
            Dictionary with:
                - success (bool): Always True (query operation)
                - recording (bool): Whether currently recording
                - playing (bool): Whether transport is playing
                - armed_tracks (list): List of track IDs armed for recording
                - armed_count (int): Number of armed tracks

        Example:
            >>> result = await recording.is_recording()
            >>> print(result)
            {'success': True, 'recording': True, 'playing': True,
             'armed_tracks': [1, 3], 'armed_count': 2}
        """
        transport = self.state.get_transport()
        armed = [
            track.strip_id
            for track in self.state.get_all_tracks().values()
            if track.rec_enabled
        ]

        logger.debug(f"Recording state: {transport.recording}, armed tracks: {len(armed)}")
        return {
            "success": True,
            "recording": transport.recording,
            "playing": transport.playing,
            "armed_tracks": armed,
            "armed_count": len(armed),
        }

    # =========================================================================
    # Punch Recording
    # =========================================================================

    async def set_punch_range(self, start_frame: int, end_frame: int) -> Dict[str, Any]:
        """
        Set punch-in/out recording range.

        Defines the frame range for punch recording. When punch-in/out
        are enabled, recording will only occur within this range.

        Args:
            start_frame: Punch-in point in frames (must be >= 0)
            end_frame: Punch-out point in frames (must be > start_frame)

        Returns:
            Dictionary with:
                - success (bool): Whether punch range was set
                - start_frame (int): Punch-in point
                - end_frame (int): Punch-out point
                - message (str): Human-readable result message

        OSC Commands:
            /set_punch_in i start_frame
            /set_punch_out i end_frame

        Example:
            >>> result = await recording.set_punch_range(48000, 96000)
            >>> print(result)
            {'success': True, 'start_frame': 48000, 'end_frame': 96000,
             'message': 'Punch range set: 48000 to 96000'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate parameters
        if start_frame < 0:
            return {"success": False, "error": f"Invalid start_frame: {start_frame} (must be >= 0)"}

        if end_frame < 0:
            return {"success": False, "error": f"Invalid end_frame: {end_frame} (must be >= 0)"}

        if start_frame >= end_frame:
            return {
                "success": False,
                "error": f"Invalid range: start_frame ({start_frame}) must be < end_frame ({end_frame})",
            }

        # Set punch-in point
        punch_in_success = self.osc.send_command("/set_punch_in", start_frame)
        if not punch_in_success:
            return {"success": False, "error": "Failed to set punch-in point"}

        # Set punch-out point
        punch_out_success = self.osc.send_command("/set_punch_out", end_frame)
        if not punch_out_success:
            return {"success": False, "error": "Failed to set punch-out point"}

        logger.info(f"Punch range set: {start_frame} to {end_frame}")
        return {
            "success": True,
            "message": f"Punch range set: {start_frame} to {end_frame}",
            "start_frame": start_frame,
            "end_frame": end_frame,
        }

    async def enable_punch_in(self) -> Dict[str, Any]:
        """
        Enable punch-in recording mode.

        When enabled, recording will automatically start at the punch-in point.
        Requires punch-in point to be set via set_punch_range().

        Returns:
            Dictionary with:
                - success (bool): Whether punch-in was enabled
                - message (str): Human-readable result message

        OSC Commands:
            /set_punch_in i 1

        Example:
            >>> result = await recording.enable_punch_in()
            >>> print(result)
            {'success': True, 'message': 'Punch-in enabled'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/set_punch_in", 1)
        if not success:
            return {"success": False, "error": "Failed to enable punch-in"}

        logger.info("Punch-in enabled")
        return {
            "success": True,
            "message": "Punch-in enabled",
        }

    async def enable_punch_out(self) -> Dict[str, Any]:
        """
        Enable punch-out recording mode.

        When enabled, recording will automatically stop at the punch-out point.
        Requires punch-out point to be set via set_punch_range().

        Returns:
            Dictionary with:
                - success (bool): Whether punch-out was enabled
                - message (str): Human-readable result message

        OSC Commands:
            /set_punch_out i 1

        Example:
            >>> result = await recording.enable_punch_out()
            >>> print(result)
            {'success': True, 'message': 'Punch-out enabled'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/set_punch_out", 1)
        if not success:
            return {"success": False, "error": "Failed to enable punch-out"}

        logger.info("Punch-out enabled")
        return {
            "success": True,
            "message": "Punch-out enabled",
        }

    async def clear_punch_range(self) -> Dict[str, Any]:
        """
        Disable both punch-in and punch-out modes.

        Clears punch recording modes. The punch-in/out points are
        retained but recording will not be limited to the punch range.

        Returns:
            Dictionary with:
                - success (bool): Whether punch modes were disabled
                - message (str): Human-readable result message

        OSC Commands:
            /set_punch_in i 0
            /set_punch_out i 0

        Example:
            >>> result = await recording.clear_punch_range()
            >>> print(result)
            {'success': True, 'message': 'Punch recording disabled'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Disable punch-in
        punch_in_success = self.osc.send_command("/set_punch_in", 0)
        if not punch_in_success:
            return {"success": False, "error": "Failed to disable punch-in"}

        # Disable punch-out
        punch_out_success = self.osc.send_command("/set_punch_out", 0)
        if not punch_out_success:
            return {"success": False, "error": "Failed to disable punch-out"}

        logger.info("Punch recording disabled")
        return {
            "success": True,
            "message": "Punch recording disabled",
        }

    # =========================================================================
    # Input Monitoring
    # =========================================================================

    async def set_input_monitoring(self, track_id: int, enabled: bool) -> Dict[str, Any]:
        """
        Enable/disable input monitoring for a track.

        Input monitoring allows you to hear the input signal in real-time,
        regardless of transport state. Useful for live monitoring while
        setting levels or when not recording.

        Args:
            track_id: Strip ID of the track (1-based integer)
            enabled: True to enable input monitoring, False to disable

        Returns:
            Dictionary with:
                - success (bool): Whether input monitoring was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - input_monitoring (bool): The new monitoring state
                - message (str): Human-readable result message

        OSC Commands:
            /strip/monitor_input ii strip_id, enabled

        Example:
            >>> result = await recording.set_input_monitoring(1, True)
            >>> print(result)
            {'success': True, 'track_id': 1, 'track_name': 'Vocals',
             'input_monitoring': True, 'message': 'Input monitoring enabled for Vocals'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Send OSC command (1 = enabled, 0 = disabled)
        monitor_value = 1 if enabled else 0
        success = self.osc.send_command("/strip/monitor_input", track_id, monitor_value)

        if success:
            action = "enabled" if enabled else "disabled"
            logger.info(f"Input monitoring {action} for track {track_id} '{track.name}'")
            return {
                "success": True,
                "message": f"Input monitoring {action} for '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "input_monitoring": enabled,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def set_disk_monitoring(self, track_id: int, enabled: bool) -> Dict[str, Any]:
        """
        Enable/disable disk monitoring for a track.

        Disk monitoring plays back the recorded audio from disk.
        This is the normal monitoring mode when not recording.

        Args:
            track_id: Strip ID of the track (1-based integer)
            enabled: True to enable disk monitoring, False to disable

        Returns:
            Dictionary with:
                - success (bool): Whether disk monitoring was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - disk_monitoring (bool): The new monitoring state
                - message (str): Human-readable result message

        OSC Commands:
            /strip/monitor_disk ii strip_id, enabled

        Example:
            >>> result = await recording.set_disk_monitoring(1, True)
            >>> print(result)
            {'success': True, 'track_id': 1, 'track_name': 'Vocals',
             'disk_monitoring': True, 'message': 'Disk monitoring enabled for Vocals'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Send OSC command (1 = enabled, 0 = disabled)
        monitor_value = 1 if enabled else 0
        success = self.osc.send_command("/strip/monitor_disk", track_id, monitor_value)

        if success:
            action = "enabled" if enabled else "disabled"
            logger.info(f"Disk monitoring {action} for track {track_id} '{track.name}'")
            return {
                "success": True,
                "message": f"Disk monitoring {action} for '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "disk_monitoring": enabled,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def set_monitoring_mode(self, track_id: int, mode: str) -> Dict[str, Any]:
        """
        Set monitoring mode for a track.

        Sets the track's monitoring mode to input, disk, or auto.
        - "input": Monitor live input signal
        - "disk": Monitor recorded audio from disk
        - "auto": Ardour automatically switches (input while recording, disk otherwise)

        Args:
            track_id: Strip ID of the track (1-based integer)
            mode: Monitoring mode ("input", "disk", or "auto")

        Returns:
            Dictionary with:
                - success (bool): Whether monitoring mode was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - mode (str): The monitoring mode set
                - message (str): Human-readable result message

        OSC Commands:
            /strip/monitor_input ii strip_id, value
            /strip/monitor_disk ii strip_id, value

        Example:
            >>> result = await recording.set_monitoring_mode(1, "input")
            >>> print(result)
            {'success': True, 'track_id': 1, 'track_name': 'Vocals',
             'mode': 'input', 'message': 'Monitoring mode set to input for Vocals'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate mode
        mode = mode.lower()
        if mode not in ("input", "disk", "auto"):
            return {
                "success": False,
                "error": f"Invalid mode: {mode}. Must be 'input', 'disk', or 'auto'",
            }

        # Check track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Set monitoring mode
        if mode == "input":
            # Enable input monitoring, disable disk
            input_success = self.osc.send_command("/strip/monitor_input", track_id, 1)
            disk_success = self.osc.send_command("/strip/monitor_disk", track_id, 0)
        elif mode == "disk":
            # Enable disk monitoring, disable input
            input_success = self.osc.send_command("/strip/monitor_input", track_id, 0)
            disk_success = self.osc.send_command("/strip/monitor_disk", track_id, 1)
        else:  # auto
            # Disable both to let Ardour manage automatically
            input_success = self.osc.send_command("/strip/monitor_input", track_id, 0)
            disk_success = self.osc.send_command("/strip/monitor_disk", track_id, 0)

        if input_success and disk_success:
            logger.info(f"Monitoring mode set to '{mode}' for track {track_id} '{track.name}'")
            return {
                "success": True,
                "message": f"Monitoring mode set to '{mode}' for '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "mode": mode,
            }

        return {"success": False, "error": "Failed to set monitoring mode"}

    # =========================================================================
    # Query Methods
    # =========================================================================

    async def get_armed_tracks(self) -> Dict[str, Any]:
        """
        List all tracks armed for recording.

        Queries cached state to find tracks with record enable active.
        Does not require OSC communication.

        Returns:
            Dictionary with:
                - success (bool): Always True (query operation)
                - armed_tracks (list): List of dicts with track info
                - armed_count (int): Number of armed tracks

        Example:
            >>> result = await recording.get_armed_tracks()
            >>> print(result)
            {'success': True, 'armed_count': 2,
             'armed_tracks': [
                {'track_id': 1, 'name': 'Vocals', 'type': 'audio'},
                {'track_id': 3, 'name': 'Guitar', 'type': 'audio'}
             ]}
        """
        tracks = self.state.get_all_tracks()
        armed = [
            {
                "track_id": track.strip_id,
                "name": track.name,
                "type": track.track_type,
            }
            for track in tracks.values()
            if track.rec_enabled
        ]

        logger.debug(f"Found {len(armed)} armed tracks")
        return {
            "success": True,
            "armed_tracks": armed,
            "armed_count": len(armed),
        }

    async def get_recording_state(self) -> Dict[str, Any]:
        """
        Get complete recording state.

        Returns comprehensive recording state including transport status,
        record enable state, and armed tracks. All from cached state.

        Returns:
            Dictionary with:
                - success (bool): Always True (query operation)
                - recording (bool): Whether currently recording
                - playing (bool): Whether transport is playing
                - armed_tracks (list): List of armed track IDs
                - armed_count (int): Number of armed tracks
                - tempo (float): Current session tempo (BPM)
                - frame (int): Current transport position in frames

        Example:
            >>> result = await recording.get_recording_state()
            >>> print(result)
            {'success': True, 'recording': True, 'playing': True,
             'armed_tracks': [1, 3], 'armed_count': 2,
             'tempo': 120.0, 'frame': 48000}
        """
        transport = self.state.get_transport()
        armed = [
            track.strip_id
            for track in self.state.get_all_tracks().values()
            if track.rec_enabled
        ]

        logger.debug(f"Recording state: recording={transport.recording}, armed={len(armed)}")
        return {
            "success": True,
            "recording": transport.recording,
            "playing": transport.playing,
            "armed_tracks": armed,
            "armed_count": len(armed),
            "tempo": transport.tempo,
            "frame": transport.frame,
        }
