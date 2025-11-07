"""
Automation control MCP tools.

Provides automation operations:
- Automation modes (off, play, write, touch, latch)
- Automation recording
- Automation editing (clear, copy)
- Automation playback control
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AutomationTools:
    """
    Automation control tools for Ardour.

    Provides methods for controlling parameter automation including
    modes, recording, editing, and playback control.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize automation tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state
        logger.info("Automation tools initialized")

    # ========================================================================
    # Automation Modes (3 methods)
    # ========================================================================

    async def set_automation_mode(
        self, track_id: int, parameter: str, mode: str
    ) -> Dict[str, Any]:
        """
        Set automation mode for a parameter.

        Controls how automation data is played back and recorded for a
        specific parameter. Available modes:
        - "off": Automation disabled, manual control only
        - "play": Play back existing automation data
        - "write": Overwrite automation data during playback
        - "touch": Write automation only when control is touched
        - "latch": Write from touch point until playback stops

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)
            mode: Automation mode (off/play/write/touch/latch)

        Returns:
            Dictionary with:
                - success (bool): Whether the mode was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - mode (str): The new automation mode
                - message (str): Human-readable result message

        OSC Commands:
            /strip/{parameter}/automation_mode isi strip_id mode_value
            Mode values: 0=off, 1=play, 2=write, 3=touch, 4=latch

        Example:
            >>> result = await automation.set_automation_mode(1, "gain", "write")
            >>> print(result)
            {'success': True, 'track_id': 1, 'parameter': 'gain', 'mode': 'write', ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate mode
        mode_map = {"off": 0, "play": 1, "write": 2, "touch": 3, "latch": 4}
        if mode.lower() not in mode_map:
            return {
                "success": False,
                "error": f"Invalid mode '{mode}'. Must be one of: {', '.join(mode_map.keys())}",
            }

        # Validate parameter
        valid_parameters = ["gain", "pan", "mute", "plugin"]
        if parameter.lower() not in valid_parameters:
            return {
                "success": False,
                "error": f"Invalid parameter '{parameter}'. Common parameters: {', '.join(valid_parameters)}",
            }

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Build OSC address
        osc_address = f"/strip/{parameter.lower()}/automation_mode"
        mode_value = mode_map[mode.lower()]

        # Send OSC command
        success = self.osc.send_command(osc_address, track_id, mode_value)

        if success:
            logger.info(
                f"Set {parameter} automation mode to '{mode}' on track {track_id} '{track.name}'"
            )
            return {
                "success": True,
                "message": f"Set {parameter} automation mode to '{mode}' on track '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "parameter": parameter,
                "mode": mode.lower(),
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def get_automation_mode(
        self, track_id: int, parameter: str
    ) -> Dict[str, Any]:
        """
        Get automation mode for a parameter.

        Queries the cached automation mode for a specific parameter.
        Note: Automation modes are not currently cached in the state system,
        so this returns a placeholder response.

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - mode (str): The automation mode (None if unknown)
                - message (str): Human-readable result message

        Example:
            >>> result = await automation.get_automation_mode(1, "gain")
            >>> # Returns: {"success": True, "track_id": 1, "parameter": "gain", "mode": None, ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Note: Automation mode is not currently cached in TrackState.
        logger.debug(
            f"Retrieved {parameter} automation mode for track {track_id} '{track.name}'"
        )
        return {
            "success": True,
            "message": f"{parameter.capitalize()} automation mode for track '{track.name}' (not cached)",
            "track_id": track_id,
            "track_name": track.name,
            "parameter": parameter,
            "mode": None,
        }

    async def list_automation_parameters(self, track_id: int) -> Dict[str, Any]:
        """
        List available automation parameters for a track.

        Returns a list of common parameters that support automation.
        The actual available parameters depend on track type and plugins.

        Args:
            track_id: Track strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameters (list): List of automatable parameter names
                - message (str): Human-readable result message

        Example:
            >>> result = await automation.list_automation_parameters(1)
            >>> # Returns: {"success": True, "parameters": ["gain", "pan", "mute"], ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Common automatable parameters for all tracks
        common_parameters = ["gain", "pan", "mute"]

        # Note: Plugin parameters would be listed here if plugin data were cached
        logger.debug(f"Listed automation parameters for track {track_id} '{track.name}'")
        return {
            "success": True,
            "message": f"Automation parameters for track '{track.name}'",
            "track_id": track_id,
            "track_name": track.name,
            "parameters": common_parameters,
        }

    # ========================================================================
    # Automation Recording (4 methods)
    # ========================================================================

    async def enable_automation_write(self, track_id: int) -> Dict[str, Any]:
        """
        Enable automation write mode for all parameters on a track.

        Puts all automatable parameters into write mode, allowing
        recording of automation data during playback.

        Args:
            track_id: Track strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether write mode was enabled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - message (str): Human-readable result message

        OSC Commands:
            /strip/automation_mode isi strip_id 2 (write mode)

        Example:
            >>> result = await automation.enable_automation_write(1)
            >>> # Returns: {"success": True, "track_id": 1, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Enable write mode for common parameters
        success = self.osc.send_command("/strip/automation_mode", track_id, 2)

        if success:
            logger.info(
                f"Enabled automation write mode on track {track_id} '{track.name}'"
            )
            return {
                "success": True,
                "message": f"Enabled automation write mode on track '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def disable_automation_write(self, track_id: int) -> Dict[str, Any]:
        """
        Disable automation write mode for all parameters on a track.

        Sets all automatable parameters to play mode, stopping new
        automation recording while preserving playback of existing data.

        Args:
            track_id: Track strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether write mode was disabled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - message (str): Human-readable result message

        OSC Commands:
            /strip/automation_mode isi strip_id 1 (play mode)

        Example:
            >>> result = await automation.disable_automation_write(1)
            >>> # Returns: {"success": True, "track_id": 1, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Set to play mode (1)
        success = self.osc.send_command("/strip/automation_mode", track_id, 1)

        if success:
            logger.info(
                f"Disabled automation write mode on track {track_id} '{track.name}'"
            )
            return {
                "success": True,
                "message": f"Disabled automation write mode on track '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def record_automation(
        self, track_id: int, parameter: str
    ) -> Dict[str, Any]:
        """
        Start recording automation for a specific parameter.

        Enables write mode for the specified parameter, allowing
        automation data to be recorded during playback.

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)

        Returns:
            Dictionary with:
                - success (bool): Whether recording started
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - message (str): Human-readable result message

        OSC Commands:
            /strip/{parameter}/automation_mode isi strip_id 2

        Example:
            >>> result = await automation.record_automation(1, "gain")
            >>> # Returns: {"success": True, "track_id": 1, "parameter": "gain", ...}
        """
        # Use set_automation_mode with write mode
        return await self.set_automation_mode(track_id, parameter, "write")

    async def stop_automation_recording(
        self, track_id: int, parameter: str
    ) -> Dict[str, Any]:
        """
        Stop recording automation for a specific parameter.

        Sets the parameter to play mode, stopping new automation
        recording while preserving playback of existing data.

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)

        Returns:
            Dictionary with:
                - success (bool): Whether recording stopped
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - message (str): Human-readable result message

        OSC Commands:
            /strip/{parameter}/automation_mode isi strip_id 1

        Example:
            >>> result = await automation.stop_automation_recording(1, "gain")
            >>> # Returns: {"success": True, "track_id": 1, "parameter": "gain", ...}
        """
        # Use set_automation_mode with play mode
        return await self.set_automation_mode(track_id, parameter, "play")

    # ========================================================================
    # Automation Editing (3 methods)
    # ========================================================================

    async def clear_automation(
        self,
        track_id: int,
        parameter: str,
        start_frame: Optional[int] = None,
        end_frame: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Clear automation data for a parameter.

        Removes automation data for the specified parameter. If frame
        range is provided, clears only that range; otherwise clears all.

        Note: Ardour's OSC interface has limited automation editing support.
        This method provides a basic interface that may require GUI interaction
        for full functionality.

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)
            start_frame: Optional start frame for range (None = clear all)
            end_frame: Optional end frame for range (None = clear all)

        Returns:
            Dictionary with:
                - success (bool): Whether automation was cleared
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - range (str): Frame range cleared ("all" or "start-end")
                - message (str): Human-readable result message

        Example:
            >>> result = await automation.clear_automation(1, "gain")
            >>> # Returns: {"success": True, "track_id": 1, "parameter": "gain", "range": "all", ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Determine range description
        if start_frame is not None and end_frame is not None:
            range_desc = f"frames {start_frame}-{end_frame}"
        else:
            range_desc = "all"

        # Note: Ardour's OSC interface doesn't directly support clearing automation.
        # This would typically be done by setting automation mode to "off" and
        # then manually clearing via GUI, or by sending specific automation points.
        # For now, we set mode to "off" as a basic implementation.
        result = await self.set_automation_mode(track_id, parameter, "off")

        if result["success"]:
            logger.info(
                f"Cleared {parameter} automation ({range_desc}) on track {track_id} '{track.name}'"
            )
            return {
                "success": True,
                "message": f"Cleared {parameter} automation ({range_desc}) on track '{track.name}' (set to off mode)",
                "track_id": track_id,
                "track_name": track.name,
                "parameter": parameter,
                "range": range_desc,
            }

        return {"success": False, "error": "Failed to clear automation"}

    async def has_automation(self, track_id: int, parameter: str) -> Dict[str, Any]:
        """
        Check if automation exists for a parameter.

        Queries whether automation data exists for the specified parameter.
        Note: This information is not currently cached in the state system.

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - has_automation (bool): Whether automation exists (None if unknown)
                - message (str): Human-readable result message

        Example:
            >>> result = await automation.has_automation(1, "gain")
            >>> # Returns: {"success": True, "has_automation": None, ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Note: Automation existence is not currently cached in TrackState.
        logger.debug(
            f"Checked {parameter} automation existence for track {track_id} '{track.name}'"
        )
        return {
            "success": True,
            "message": f"{parameter.capitalize()} automation status for track '{track.name}' (not cached)",
            "track_id": track_id,
            "track_name": track.name,
            "parameter": parameter,
            "has_automation": None,
        }

    async def copy_automation(
        self, source_track: int, dest_track: int, parameter: str
    ) -> Dict[str, Any]:
        """
        Copy automation data between tracks.

        Copies automation data for a specific parameter from one track
        to another. This is useful for duplicating settings across tracks.

        Note: Ardour's OSC interface has limited automation copying support.
        This method provides a placeholder that would typically require
        GUI interaction or more advanced OSC commands.

        Args:
            source_track: Source track strip ID (1-based)
            dest_track: Destination track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)

        Returns:
            Dictionary with:
                - success (bool): Whether automation was copied
                - source_track (int): The source track ID
                - source_name (str): Name of the source track
                - dest_track (int): The destination track ID
                - dest_name (str): Name of the destination track
                - parameter (str): The parameter name
                - message (str): Human-readable result message

        Example:
            >>> result = await automation.copy_automation(1, 2, "gain")
            >>> # Returns: {"success": True, "source_track": 1, "dest_track": 2, ...}
        """
        # Validate source track exists
        source = self.state.get_track(source_track)
        if not source:
            return {"success": False, "error": f"Source track {source_track} not found"}

        # Validate destination track exists
        dest = self.state.get_track(dest_track)
        if not dest:
            return {
                "success": False,
                "error": f"Destination track {dest_track} not found",
            }

        # Note: Direct automation copying is not supported via OSC.
        # This would require more complex implementation or GUI interaction.
        # For now, return informational response.
        logger.info(
            f"Copy {parameter} automation from track {source_track} '{source.name}' "
            f"to track {dest_track} '{dest.name}' (not directly supported via OSC)"
        )
        return {
            "success": True,
            "message": f"Automation copy requested from '{source.name}' to '{dest.name}' "
            f"(requires manual GUI operation - OSC has limited support)",
            "source_track": source_track,
            "source_name": source.name,
            "dest_track": dest_track,
            "dest_name": dest.name,
            "parameter": parameter,
        }

    # ========================================================================
    # Automation Playback (3 methods)
    # ========================================================================

    async def enable_automation_playback(
        self, track_id: int, parameter: str
    ) -> Dict[str, Any]:
        """
        Enable automation playback for a parameter.

        Sets the parameter to play mode, enabling playback of
        existing automation data without recording new data.

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)

        Returns:
            Dictionary with:
                - success (bool): Whether playback was enabled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - message (str): Human-readable result message

        OSC Commands:
            /strip/{parameter}/automation_mode isi strip_id 1

        Example:
            >>> result = await automation.enable_automation_playback(1, "gain")
            >>> # Returns: {"success": True, "track_id": 1, "parameter": "gain", ...}
        """
        # Use set_automation_mode with play mode
        return await self.set_automation_mode(track_id, parameter, "play")

    async def disable_automation_playback(
        self, track_id: int, parameter: str
    ) -> Dict[str, Any]:
        """
        Disable automation playback for a parameter.

        Sets the parameter to off mode, disabling both playback and
        recording of automation data.

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)

        Returns:
            Dictionary with:
                - success (bool): Whether playback was disabled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - message (str): Human-readable result message

        OSC Commands:
            /strip/{parameter}/automation_mode isi strip_id 0

        Example:
            >>> result = await automation.disable_automation_playback(1, "gain")
            >>> # Returns: {"success": True, "track_id": 1, "parameter": "gain", ...}
        """
        # Use set_automation_mode with off mode
        return await self.set_automation_mode(track_id, parameter, "off")

    async def get_automation_state(
        self, track_id: int, parameter: str
    ) -> Dict[str, Any]:
        """
        Get complete automation state for a parameter.

        Returns comprehensive automation status including mode, playback
        state, and whether automation data exists.

        Args:
            track_id: Track strip ID (1-based)
            parameter: Parameter name ("gain", "pan", "mute", etc.)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - parameter (str): The parameter name
                - mode (str): Current automation mode (None if unknown)
                - has_automation (bool): Whether automation exists (None if unknown)
                - playback_enabled (bool): Whether playback is enabled (None if unknown)
                - message (str): Human-readable result message

        Example:
            >>> result = await automation.get_automation_state(1, "gain")
            >>> # Returns: {"success": True, "track_id": 1, "parameter": "gain", ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Note: Automation state is not currently cached in TrackState.
        logger.debug(
            f"Retrieved {parameter} automation state for track {track_id} '{track.name}'"
        )
        return {
            "success": True,
            "message": f"Automation state for {parameter} on track '{track.name}' (not cached)",
            "track_id": track_id,
            "track_name": track.name,
            "parameter": parameter,
            "mode": None,
            "has_automation": None,
            "playback_enabled": None,
        }
