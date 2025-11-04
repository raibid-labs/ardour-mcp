"""
Session information MCP tools.

Provides tools for querying session information:
- Session details (name, sample rate, tempo)
- Marker lists
- Session statistics
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SessionTools:
    """
    Session information tools for Ardour.

    Provides methods for querying session state and information.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize session tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state
        logger.info("Session tools initialized")

    async def get_session_info(self) -> Dict[str, Any]:
        """
        Get complete session information.

        Returns:
            Dictionary with session details
        """
        session = self.state.get_session_info()
        transport = session.transport

        return {
            "success": True,
            "session_name": session.name,
            "session_path": session.path,
            "sample_rate": session.sample_rate,
            "tempo": transport.tempo,
            "time_signature": f"{transport.time_signature[0]}/{transport.time_signature[1]}",
            "track_count": len(session.tracks),
            "marker_count": len(session.markers),
            "dirty": session.dirty,
            "playing": transport.playing,
            "recording": transport.recording,
            "frame": transport.frame,
        }

    async def get_tempo(self) -> Dict[str, Any]:
        """
        Get current session tempo.

        Returns:
            Dictionary with tempo (BPM)
        """
        transport = self.state.get_transport()

        return {
            "success": True,
            "tempo": transport.tempo,
            "message": f"Current tempo: {transport.tempo} BPM",
        }

    async def get_time_signature(self) -> Dict[str, Any]:
        """
        Get current time signature.

        Returns:
            Dictionary with time signature
        """
        transport = self.state.get_transport()
        beats, beat_type = transport.time_signature

        return {
            "success": True,
            "time_signature": f"{beats}/{beat_type}",
            "beats_per_bar": beats,
            "beat_type": beat_type,
            "message": f"Time signature: {beats}/{beat_type}",
        }

    async def get_sample_rate(self) -> Dict[str, Any]:
        """
        Get session sample rate.

        Returns:
            Dictionary with sample rate
        """
        session = self.state.get_session_info()

        return {
            "success": True,
            "sample_rate": session.sample_rate,
            "message": f"Sample rate: {session.sample_rate} Hz",
        }

    async def list_markers(self) -> Dict[str, Any]:
        """
        List all markers in the session.

        Returns:
            Dictionary with list of markers
        """
        session = self.state.get_session_info()

        markers = [{"name": name, "frame": frame} for name, frame in session.markers]

        return {
            "success": True,
            "marker_count": len(markers),
            "markers": markers,
        }

    async def save_session(self) -> Dict[str, Any]:
        """
        Save the current session.

        Returns:
            Dictionary with success status
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        success = self.osc.send_command("/save_state")

        return {
            "success": success,
            "message": "Session saved" if success else "Failed to save session",
        }

    async def get_track_count(self) -> Dict[str, Any]:
        """
        Get number of tracks in session.

        Returns:
            Dictionary with track count
        """
        tracks = self.state.get_all_tracks()

        return {
            "success": True,
            "track_count": len(tracks),
            "message": f"Session has {len(tracks)} tracks",
        }

    async def is_session_dirty(self) -> Dict[str, Any]:
        """
        Check if session has unsaved changes.

        Returns:
            Dictionary with dirty flag
        """
        session = self.state.get_session_info()

        return {
            "success": True,
            "dirty": session.dirty,
            "message": "Session has unsaved changes" if session.dirty else "Session is saved",
        }
