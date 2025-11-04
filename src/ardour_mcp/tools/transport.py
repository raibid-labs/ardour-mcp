"""
Transport control MCP tools.

Provides tools for controlling Ardour's transport:
- Play/stop/record
- Navigation (start, end, markers)
- Position queries
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class TransportTools:
    """
    Transport control tools for Ardour.

    Provides methods for controlling playback, recording, and navigation.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize transport tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state
        logger.info("Transport tools initialized")

    async def transport_play(self) -> Dict[str, Any]:
        """
        Start playback in Ardour.

        Returns:
            Dictionary with success status and current state
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/transport_play")
        transport = self.state.get_transport()

        return {
            "success": success,
            "playing": transport.playing,
            "frame": transport.frame,
            "message": "Playback started" if success else "Failed to start playback",
        }

    async def transport_stop(self) -> Dict[str, Any]:
        """
        Stop playback in Ardour.

        Returns:
            Dictionary with success status and current state
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/transport_stop")
        transport = self.state.get_transport()

        return {
            "success": success,
            "playing": transport.playing,
            "frame": transport.frame,
            "message": "Playback stopped" if success else "Failed to stop playback",
        }

    async def transport_pause(self) -> Dict[str, Any]:
        """
        Toggle pause in Ardour.

        Returns:
            Dictionary with success status
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/transport_pause")
        return {
            "success": success,
            "message": "Playback paused/resumed" if success else "Failed to pause",
        }

    async def toggle_record(self) -> Dict[str, Any]:
        """
        Toggle global recording in Ardour.

        Returns:
            Dictionary with success status and recording state
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/rec_enable_toggle")
        transport = self.state.get_transport()

        return {
            "success": success,
            "recording": transport.recording,
            "message": "Recording toggled" if success else "Failed to toggle recording",
        }

    async def goto_start(self) -> Dict[str, Any]:
        """
        Jump to session start.

        Returns:
            Dictionary with success status
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/goto_start")
        return {
            "success": success,
            "message": "Jumped to start" if success else "Failed to goto start",
        }

    async def goto_end(self) -> Dict[str, Any]:
        """
        Jump to session end.

        Returns:
            Dictionary with success status
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/goto_end")
        return {
            "success": success,
            "message": "Jumped to end" if success else "Failed to goto end",
        }

    async def goto_marker(self, marker_name: str) -> Dict[str, Any]:
        """
        Jump to a named marker.

        Args:
            marker_name: Name of the marker to jump to

        Returns:
            Dictionary with success status
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if not marker_name:
            return {"success": False, "error": "Marker name required"}

        success = self.osc.send_command("/locate", marker_name)
        return {
            "success": success,
            "marker": marker_name,
            "message": f"Jumped to marker '{marker_name}'"
            if success
            else f"Failed to jump to marker '{marker_name}'",
        }

    async def locate(self, frame: int) -> Dict[str, Any]:
        """
        Jump to a specific frame position.

        Args:
            frame: Frame number to jump to

        Returns:
            Dictionary with success status and new position
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if frame < 0:
            return {"success": False, "error": "Frame must be non-negative"}

        success = self.osc.send_command("/locate", frame)
        transport = self.state.get_transport()

        return {
            "success": success,
            "frame": transport.frame,
            "message": f"Located to frame {frame}" if success else "Failed to locate",
        }

    async def set_loop_range(self, start_frame: int, end_frame: int) -> Dict[str, Any]:
        """
        Set loop range.

        Args:
            start_frame: Loop start frame
            end_frame: Loop end frame

        Returns:
            Dictionary with success status
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if start_frame < 0 or end_frame < 0:
            return {"success": False, "error": "Frame values must be non-negative"}

        if end_frame <= start_frame:
            return {"success": False, "error": "End frame must be after start frame"}

        success = self.osc.send_command("/set_loop_range", start_frame, end_frame)
        return {
            "success": success,
            "loop_start": start_frame,
            "loop_end": end_frame,
            "message": f"Loop range set: {start_frame} to {end_frame}"
            if success
            else "Failed to set loop range",
        }

    async def toggle_loop(self) -> Dict[str, Any]:
        """
        Toggle loop mode.

        Returns:
            Dictionary with success status and loop state
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/loop_toggle")
        transport = self.state.get_transport()

        return {
            "success": success,
            "loop_enabled": transport.loop_enabled,
            "message": "Loop toggled" if success else "Failed to toggle loop",
        }

    async def get_transport_position(self) -> Dict[str, Any]:
        """
        Get current transport position and state.

        Returns:
            Dictionary with transport information
        """
        transport = self.state.get_transport()

        return {
            "success": True,
            "playing": transport.playing,
            "recording": transport.recording,
            "frame": transport.frame,
            "tempo": transport.tempo,
            "time_signature": f"{transport.time_signature[0]}/{transport.time_signature[1]}",
            "loop_enabled": transport.loop_enabled,
        }

    async def set_tempo(self, bpm: float) -> Dict[str, Any]:
        """
        Set session tempo.

        Args:
            bpm: Tempo in beats per minute

        Returns:
            Dictionary with success status
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if bpm <= 0 or bpm > 300:
            return {"success": False, "error": "Tempo must be between 1 and 300 BPM"}

        # Note: Ardour doesn't have a direct OSC command for tempo
        # This would typically be done via /set_surface for tempo changes
        # For now, we'll return an informative message
        return {
            "success": False,
            "error": "Tempo setting not directly supported via OSC",
            "message": "Use Ardour's tempo map for tempo changes",
        }
