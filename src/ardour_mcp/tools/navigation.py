"""
Navigation control MCP tools.

Provides tools for navigation operations:
- Marker management (create, delete, rename, goto)
- Loop control (set range, enable/disable, clear)
- Tempo and time signature control
- Navigation helpers (goto time, bar, skip)
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class NavigationTools:
    """
    Navigation control tools for Ardour.

    Provides methods for controlling markers, loop ranges, tempo,
    time signature, and various navigation operations.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize navigation tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state
        logger.info("Navigation tools initialized")

    # ==================== Marker Management ====================

    async def create_marker(self, name: str, position: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a marker at specified position or current position.

        Markers are named locations in the timeline that can be used for
        navigation and organization. If no position is specified, the marker
        is created at the current transport position.

        Args:
            name: Name for the new marker
            position: Position in frames (None = current position)

        Returns:
            Dictionary with:
                - success (bool): Whether the marker was created
                - marker_name (str): Name of the created marker
                - position (int): Position where marker was created (if known)
                - message (str): Human-readable result message

        OSC Commands:
            /add_marker s name (adds at current position)
            OR
            /locate ii frame, force then /add_marker s name

        Example:
            >>> result = await nav.create_marker("Verse 1")
            >>> # Returns: {'success': True, 'marker_name': 'Verse 1', 'message': 'Created marker...'}
            >>> result = await nav.create_marker("Chorus", 480000)
            >>> # Returns: {'success': True, 'marker_name': 'Chorus', 'position': 480000, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if not name or not name.strip():
            return {"success": False, "error": "Marker name cannot be empty"}

        # If position is specified, locate to that position first
        if position is not None:
            if position < 0:
                return {"success": False, "error": "Position must be non-negative"}

            # Locate to the position with force flag
            locate_success = self.osc.send_command("/locate", position, 1)
            if not locate_success:
                return {
                    "success": False,
                    "error": f"Failed to locate to frame {position}",
                }

        # Create marker at current position
        success = self.osc.send_command("/add_marker", name)

        if success:
            message = f"Created marker '{name}'"
            result = {
                "success": True,
                "message": message,
                "marker_name": name,
            }
            if position is not None:
                result["position"] = position
                message += f" at frame {position}"
                result["message"] = message

            logger.info(message)
            return result

        return {"success": False, "error": "Failed to create marker"}

    async def delete_marker(self, name: str) -> Dict[str, Any]:
        """
        Delete a marker by name.

        Removes the specified marker from the session timeline.

        Args:
            name: Name of the marker to delete

        Returns:
            Dictionary with:
                - success (bool): Whether the marker was deleted
                - marker_name (str): Name of the deleted marker
                - message (str): Human-readable result message

        OSC Commands:
            /remove_marker s name

        Example:
            >>> result = await nav.delete_marker("Verse 1")
            >>> # Returns: {'success': True, 'marker_name': 'Verse 1', 'message': 'Deleted marker...'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if not name or not name.strip():
            return {"success": False, "error": "Marker name cannot be empty"}

        # Send OSC command to remove marker
        success = self.osc.send_command("/remove_marker", name)

        if success:
            logger.info(f"Deleted marker '{name}'")
            return {
                "success": True,
                "message": f"Deleted marker '{name}'",
                "marker_name": name,
            }

        return {"success": False, "error": f"Failed to delete marker '{name}'"}

    async def rename_marker(self, old_name: str, new_name: str) -> Dict[str, Any]:
        """
        Rename a marker.

        Changes the name of an existing marker. This is implemented by
        getting the marker's position, deleting the old marker, and
        creating a new one at the same position.

        Args:
            old_name: Current name of the marker
            new_name: New name for the marker

        Returns:
            Dictionary with:
                - success (bool): Whether the marker was renamed
                - old_name (str): Original marker name
                - new_name (str): New marker name
                - message (str): Human-readable result message

        OSC Commands:
            Uses get_marker_position, delete_marker, and create_marker

        Example:
            >>> result = await nav.rename_marker("Verse", "Verse 1")
            >>> # Returns: {'success': True, 'old_name': 'Verse', 'new_name': 'Verse 1', ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if not old_name or not old_name.strip():
            return {"success": False, "error": "Old marker name cannot be empty"}

        if not new_name or not new_name.strip():
            return {"success": False, "error": "New marker name cannot be empty"}

        # Get the position of the old marker
        marker_pos_result = await self.get_marker_position(old_name)
        if not marker_pos_result["success"]:
            return {
                "success": False,
                "error": f"Marker '{old_name}' not found",
            }

        position = marker_pos_result.get("position")

        # Delete the old marker
        delete_result = await self.delete_marker(old_name)
        if not delete_result["success"]:
            return {
                "success": False,
                "error": f"Failed to delete old marker '{old_name}'",
            }

        # Create new marker at same position
        create_result = await self.create_marker(new_name, position)
        if not create_result["success"]:
            # Try to restore the old marker if creation failed
            await self.create_marker(old_name, position)
            return {
                "success": False,
                "error": f"Failed to create new marker '{new_name}'",
            }

        logger.info(f"Renamed marker '{old_name}' to '{new_name}'")
        return {
            "success": True,
            "message": f"Renamed marker '{old_name}' to '{new_name}'",
            "old_name": old_name,
            "new_name": new_name,
        }

    async def goto_marker(self, name: str) -> Dict[str, Any]:
        """
        Jump to a named marker.

        Moves the transport position to the location of the specified marker.

        Args:
            name: Name of the marker to jump to

        Returns:
            Dictionary with:
                - success (bool): Whether transport moved to marker
                - marker_name (str): Name of the marker
                - message (str): Human-readable result message

        OSC Commands:
            /locate s marker_name

        Example:
            >>> result = await nav.goto_marker("Chorus")
            >>> # Returns: {'success': True, 'marker_name': 'Chorus', 'message': 'Jumped to marker...'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if not name or not name.strip():
            return {"success": False, "error": "Marker name cannot be empty"}

        # Send OSC command to locate to marker
        success = self.osc.send_command("/locate", name)

        if success:
            logger.info(f"Jumped to marker '{name}'")
            return {
                "success": True,
                "message": f"Jumped to marker '{name}'",
                "marker_name": name,
            }

        return {"success": False, "error": f"Failed to jump to marker '{name}'"}

    async def get_marker_position(self, name: str) -> Dict[str, Any]:
        """
        Get the position of a named marker.

        Queries the cached state for the marker's position in frames.

        Args:
            name: Name of the marker to query

        Returns:
            Dictionary with:
                - success (bool): Whether the marker was found
                - marker_name (str): Name of the marker
                - position (int): Position in frames
                - message (str): Human-readable result message

        Example:
            >>> result = await nav.get_marker_position("Verse 1")
            >>> # Returns: {'success': True, 'marker_name': 'Verse 1', 'position': 240000, ...}
        """
        if not name or not name.strip():
            return {"success": False, "error": "Marker name cannot be empty"}

        # Get markers from cached state
        session = self.state.get_session_info()
        markers = session.markers

        # Find the marker by name
        for marker_name, marker_position in markers:
            if marker_name == name:
                logger.debug(f"Found marker '{name}' at position {marker_position}")
                return {
                    "success": True,
                    "marker_name": name,
                    "position": marker_position,
                    "message": f"Marker '{name}' is at frame {marker_position}",
                }

        return {
            "success": False,
            "error": f"Marker '{name}' not found in session",
        }

    # ==================== Loop Control ====================

    async def set_loop_range(self, start_frame: int, end_frame: int) -> Dict[str, Any]:
        """
        Set loop range.

        Defines the start and end points for loop playback.
        The loop must be enabled separately using enable_loop().

        Args:
            start_frame: Loop start position in frames
            end_frame: Loop end position in frames

        Returns:
            Dictionary with:
                - success (bool): Whether the loop range was set
                - loop_start (int): Loop start frame
                - loop_end (int): Loop end frame
                - message (str): Human-readable result message

        OSC Commands:
            /set_loop_range ii start, end

        Example:
            >>> result = await nav.set_loop_range(48000, 96000)
            >>> # Returns: {'success': True, 'loop_start': 48000, 'loop_end': 96000, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if start_frame < 0 or end_frame < 0:
            return {"success": False, "error": "Frame values must be non-negative"}

        if end_frame <= start_frame:
            return {"success": False, "error": "End frame must be after start frame"}

        # Send OSC command to set loop range
        success = self.osc.send_command("/set_loop_range", start_frame, end_frame)

        if success:
            logger.info(f"Set loop range: {start_frame} to {end_frame}")
            return {
                "success": True,
                "message": f"Loop range set: {start_frame} to {end_frame}",
                "loop_start": start_frame,
                "loop_end": end_frame,
            }

        return {"success": False, "error": "Failed to set loop range"}

    async def enable_loop(self) -> Dict[str, Any]:
        """
        Enable loop playback.

        Enables looping at the current loop range. If loop is already
        enabled, this command has no effect.

        Returns:
            Dictionary with:
                - success (bool): Whether loop was enabled
                - loop_enabled (bool): Current loop state (True)
                - message (str): Human-readable result message

        OSC Commands:
            /loop_toggle (if not already looping)

        Example:
            >>> result = await nav.enable_loop()
            >>> # Returns: {'success': True, 'loop_enabled': True, 'message': 'Loop enabled'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check current loop state
        transport = self.state.get_transport()
        if transport.loop_enabled:
            # Already looping, no need to toggle
            logger.debug("Loop already enabled")
            return {
                "success": True,
                "message": "Loop already enabled",
                "loop_enabled": True,
            }

        # Toggle loop to enable it
        success = self.osc.send_command("/loop_toggle")

        if success:
            logger.info("Loop enabled")
            return {
                "success": True,
                "message": "Loop enabled",
                "loop_enabled": True,
            }

        return {"success": False, "error": "Failed to enable loop"}

    async def disable_loop(self) -> Dict[str, Any]:
        """
        Disable loop playback.

        Disables looping. If loop is already disabled, this command
        has no effect.

        Returns:
            Dictionary with:
                - success (bool): Whether loop was disabled
                - loop_enabled (bool): Current loop state (False)
                - message (str): Human-readable result message

        OSC Commands:
            /loop_toggle (if currently looping)

        Example:
            >>> result = await nav.disable_loop()
            >>> # Returns: {'success': True, 'loop_enabled': False, 'message': 'Loop disabled'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check current loop state
        transport = self.state.get_transport()
        if not transport.loop_enabled:
            # Already not looping, no need to toggle
            logger.debug("Loop already disabled")
            return {
                "success": True,
                "message": "Loop already disabled",
                "loop_enabled": False,
            }

        # Toggle loop to disable it
        success = self.osc.send_command("/loop_toggle")

        if success:
            logger.info("Loop disabled")
            return {
                "success": True,
                "message": "Loop disabled",
                "loop_enabled": False,
            }

        return {"success": False, "error": "Failed to disable loop"}

    async def clear_loop_range(self) -> Dict[str, Any]:
        """
        Clear loop range and disable looping.

        Disables loop playback and clears the loop range.
        This is equivalent to disabling loop mode.

        Returns:
            Dictionary with:
                - success (bool): Whether loop was cleared
                - loop_enabled (bool): Current loop state (False)
                - message (str): Human-readable result message

        OSC Commands:
            /loop_toggle (if currently looping)

        Example:
            >>> result = await nav.clear_loop_range()
            >>> # Returns: {'success': True, 'loop_enabled': False, 'message': 'Loop cleared'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Disable loop
        result = await self.disable_loop()

        if result["success"]:
            result["message"] = "Loop range cleared"
            logger.info("Loop range cleared")

        return result

    # ==================== Tempo & Time Signature ====================

    async def set_tempo(self, bpm: float) -> Dict[str, Any]:
        """
        Set session tempo in beats per minute.

        Changes the global tempo for the session. Ardour supports tempos
        from 20.0 to 300.0 BPM.

        Args:
            bpm: Tempo in BPM (range: 20.0 to 300.0)

        Returns:
            Dictionary with:
                - success (bool): Whether the tempo was set
                - tempo (float): The new tempo in BPM
                - message (str): Human-readable result message

        OSC Commands:
            /set_tempo f bpm

        Example:
            >>> result = await nav.set_tempo(120.0)
            >>> # Returns: {'success': True, 'tempo': 120.0, 'message': 'Tempo set to 120.0 BPM'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate range
        if not 20.0 <= bpm <= 300.0:
            return {
                "success": False,
                "error": f"Tempo {bpm} BPM out of range (20.0 to 300.0)",
            }

        # Send OSC command
        success = self.osc.send_command("/set_tempo", bpm)

        if success:
            logger.info(f"Set tempo to {bpm} BPM")
            return {
                "success": True,
                "message": f"Tempo set to {bpm} BPM",
                "tempo": bpm,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def get_tempo(self) -> Dict[str, Any]:
        """
        Get current session tempo.

        Queries the cached state for the current tempo.
        Does not require OSC communication.

        Returns:
            Dictionary with:
                - success (bool): Always True
                - tempo (float): Current tempo in BPM
                - message (str): Human-readable result message

        Example:
            >>> result = await nav.get_tempo()
            >>> # Returns: {'success': True, 'tempo': 120.0, 'message': 'Current tempo: 120.0 BPM'}
        """
        transport = self.state.get_transport()
        tempo = transport.tempo

        logger.debug(f"Current tempo: {tempo} BPM")
        return {
            "success": True,
            "tempo": tempo,
            "message": f"Current tempo: {tempo} BPM",
        }

    async def set_time_signature(self, numerator: int, denominator: int) -> Dict[str, Any]:
        """
        Set time signature.

        Changes the time signature for the session. Common time signatures
        include 4/4, 3/4, 6/8, etc.

        Args:
            numerator: Beats per bar (e.g., 4 in 4/4 time)
            denominator: Note value per beat (e.g., 4 in 4/4 time)

        Returns:
            Dictionary with:
                - success (bool): Whether the time signature was set
                - time_signature (str): The new time signature (e.g., "4/4")
                - message (str): Human-readable result message

        OSC Commands:
            /set_time_signature ii numerator, denominator

        Example:
            >>> result = await nav.set_time_signature(3, 4)
            >>> # Returns: {'success': True, 'time_signature': '3/4', 'message': 'Time signature set to 3/4'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate numerator and denominator
        if numerator < 1 or numerator > 32:
            return {
                "success": False,
                "error": f"Numerator {numerator} out of range (1 to 32)",
            }

        valid_denominators = [1, 2, 4, 8, 16, 32]
        if denominator not in valid_denominators:
            return {
                "success": False,
                "error": f"Denominator {denominator} must be one of {valid_denominators}",
            }

        # Send OSC command
        success = self.osc.send_command("/set_time_signature", numerator, denominator)

        if success:
            time_sig = f"{numerator}/{denominator}"
            logger.info(f"Set time signature to {time_sig}")
            return {
                "success": True,
                "message": f"Time signature set to {time_sig}",
                "time_signature": time_sig,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def get_time_signature(self) -> Dict[str, Any]:
        """
        Get current time signature.

        Queries the cached state for the current time signature.
        Does not require OSC communication.

        Returns:
            Dictionary with:
                - success (bool): Always True
                - time_signature (str): Current time signature (e.g., "4/4")
                - numerator (int): Beats per bar
                - denominator (int): Note value per beat
                - message (str): Human-readable result message

        Example:
            >>> result = await nav.get_time_signature()
            >>> # Returns: {'success': True, 'time_signature': '4/4', 'numerator': 4, 'denominator': 4, ...}
        """
        transport = self.state.get_transport()
        numerator, denominator = transport.time_signature
        time_sig = f"{numerator}/{denominator}"

        logger.debug(f"Current time signature: {time_sig}")
        return {
            "success": True,
            "time_signature": time_sig,
            "numerator": numerator,
            "denominator": denominator,
            "message": f"Current time signature: {time_sig}",
        }

    # ==================== Navigation Helpers ====================

    def _timecode_to_frames(self, hours: int, minutes: int, seconds: int, frames: int) -> int:
        """
        Convert timecode to frame number.

        Args:
            hours: Hours component
            minutes: Minutes component
            seconds: Seconds component
            frames: Frame component

        Returns:
            Total frame number
        """
        sample_rate = self.state.get_session_info().sample_rate or 48000
        total_seconds = (hours * 3600) + (minutes * 60) + seconds
        return int((total_seconds * sample_rate) + frames)

    def _bar_to_frames(self, bar_number: int) -> int:
        """
        Convert bar number to frame number (approximate).

        Args:
            bar_number: Bar number (1-based)

        Returns:
            Approximate frame number for the start of the bar
        """
        transport = self.state.get_transport()
        tempo = transport.tempo or 120.0
        numerator, _ = transport.time_signature or (4, 4)

        # Calculate beats per bar
        beats_per_bar = numerator

        # Calculate seconds per bar
        seconds_per_beat = 60.0 / tempo
        seconds_per_bar = seconds_per_beat * beats_per_bar

        # Convert to frames
        sample_rate = self.state.get_session_info().sample_rate or 48000
        seconds = (bar_number - 1) * seconds_per_bar  # bar_number starts at 1
        return int(seconds * sample_rate)

    async def goto_time(
        self, hours: int, minutes: int, seconds: int, frames: int = 0
    ) -> Dict[str, Any]:
        """
        Jump to a specific timecode position.

        Converts timecode (hours:minutes:seconds:frames) to a frame number
        and moves the transport to that position.

        Args:
            hours: Hours component (0-23)
            minutes: Minutes component (0-59)
            seconds: Seconds component (0-59)
            frames: Frame component (default: 0)

        Returns:
            Dictionary with:
                - success (bool): Whether transport moved to position
                - timecode (str): Timecode as string (HH:MM:SS:FF)
                - frame (int): Frame position
                - message (str): Human-readable result message

        OSC Commands:
            /locate ii frame, force

        Example:
            >>> result = await nav.goto_time(0, 1, 30, 0)
            >>> # Returns: {'success': True, 'timecode': '00:01:30:00', 'frame': 72000, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate timecode components
        if hours < 0 or minutes < 0 or seconds < 0 or frames < 0:
            return {"success": False, "error": "Timecode components must be non-negative"}

        if minutes > 59:
            return {"success": False, "error": "Minutes must be 0-59"}

        if seconds > 59:
            return {"success": False, "error": "Seconds must be 0-59"}

        # Convert to frame number
        frame_number = self._timecode_to_frames(hours, minutes, seconds, frames)

        # Send OSC command to locate
        success = self.osc.send_command("/locate", frame_number, 1)

        if success:
            timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
            logger.info(f"Jumped to timecode {timecode} (frame {frame_number})")
            return {
                "success": True,
                "message": f"Jumped to timecode {timecode}",
                "timecode": timecode,
                "frame": frame_number,
            }

        return {"success": False, "error": "Failed to locate to timecode"}

    async def goto_bar(self, bar_number: int) -> Dict[str, Any]:
        """
        Jump to a specific bar number.

        Calculates the frame position for the start of the specified bar
        based on the current tempo and time signature, then moves the
        transport to that position.

        Args:
            bar_number: Bar number to jump to (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether transport moved to bar
                - bar (int): Bar number
                - frame (int): Frame position
                - message (str): Human-readable result message

        OSC Commands:
            /locate ii frame, force

        Example:
            >>> result = await nav.goto_bar(5)
            >>> # Returns: {'success': True, 'bar': 5, 'frame': 192000, 'message': 'Jumped to bar 5'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if bar_number < 1:
            return {"success": False, "error": "Bar number must be positive (1-based)"}

        # Calculate frame position for the bar
        frame_number = self._bar_to_frames(bar_number)

        # Send OSC command to locate
        success = self.osc.send_command("/locate", frame_number, 1)

        if success:
            logger.info(f"Jumped to bar {bar_number} (frame {frame_number})")
            return {
                "success": True,
                "message": f"Jumped to bar {bar_number}",
                "bar": bar_number,
                "frame": frame_number,
            }

        return {"success": False, "error": f"Failed to jump to bar {bar_number}"}

    async def skip_forward(self, seconds: float) -> Dict[str, Any]:
        """
        Skip forward by specified number of seconds.

        Moves the transport position forward by the specified duration.

        Args:
            seconds: Number of seconds to skip forward

        Returns:
            Dictionary with:
                - success (bool): Whether transport moved forward
                - seconds (float): Number of seconds skipped
                - frame (int): New frame position
                - message (str): Human-readable result message

        OSC Commands:
            /locate ii frame, force

        Example:
            >>> result = await nav.skip_forward(10.0)
            >>> # Returns: {'success': True, 'seconds': 10.0, 'frame': 528000, 'message': 'Skipped forward 10.0 seconds'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if seconds < 0:
            return {"success": False, "error": "Seconds must be non-negative"}

        # Get current position
        transport = self.state.get_transport()
        current_frame = transport.frame

        # Calculate new position
        sample_rate = self.state.get_session_info().sample_rate or 48000
        frame_offset = int(seconds * sample_rate)
        new_frame = current_frame + frame_offset

        # Send OSC command to locate
        success = self.osc.send_command("/locate", new_frame, 1)

        if success:
            logger.info(f"Skipped forward {seconds} seconds to frame {new_frame}")
            return {
                "success": True,
                "message": f"Skipped forward {seconds} seconds",
                "seconds": seconds,
                "frame": new_frame,
            }

        return {"success": False, "error": "Failed to skip forward"}

    async def skip_backward(self, seconds: float) -> Dict[str, Any]:
        """
        Skip backward by specified number of seconds.

        Moves the transport position backward by the specified duration.
        Will not go before frame 0.

        Args:
            seconds: Number of seconds to skip backward

        Returns:
            Dictionary with:
                - success (bool): Whether transport moved backward
                - seconds (float): Number of seconds skipped
                - frame (int): New frame position
                - message (str): Human-readable result message

        OSC Commands:
            /locate ii frame, force

        Example:
            >>> result = await nav.skip_backward(5.0)
            >>> # Returns: {'success': True, 'seconds': 5.0, 'frame': 288000, 'message': 'Skipped backward 5.0 seconds'}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if seconds < 0:
            return {"success": False, "error": "Seconds must be non-negative"}

        # Get current position
        transport = self.state.get_transport()
        current_frame = transport.frame

        # Calculate new position (don't go below 0)
        sample_rate = self.state.get_session_info().sample_rate or 48000
        frame_offset = int(seconds * sample_rate)
        new_frame = max(0, current_frame - frame_offset)

        # Send OSC command to locate
        success = self.osc.send_command("/locate", new_frame, 1)

        if success:
            logger.info(f"Skipped backward {seconds} seconds to frame {new_frame}")
            return {
                "success": True,
                "message": f"Skipped backward {seconds} seconds",
                "seconds": seconds,
                "frame": new_frame,
            }

        return {"success": False, "error": "Failed to skip backward"}
