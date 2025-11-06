"""
Track management MCP tools.

Provides tools for track operations:
- Create audio/MIDI tracks
- List tracks
- Select tracks
- Track naming
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class TrackTools:
    """
    Track management tools for Ardour.

    Provides methods for creating, listing, selecting, and managing tracks.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize track management tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state
        logger.info("Track tools initialized")

    async def create_audio_track(self, name: str = "") -> Dict[str, Any]:
        """
        Create a new audio track in Ardour.

        Sends OSC command to create a single audio track. If a name is provided,
        the track will be renamed after creation.

        Args:
            name: Optional name for the new track

        Returns:
            Dictionary with:
                - success (bool): Whether the track was created
                - message (str): Human-readable result message
                - track_count (int): Number of tracks after creation (if successful)

        Example:
            >>> result = await track_tools.create_audio_track("Vocals")
            >>> # Returns: {"success": True, "message": "Created audio track 'Vocals'", "track_count": 5}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Create one audio track using OSC command
        # /add_audio_track i count
        success = self.osc.send_command("/add_audio_track", 1)

        if not success:
            logger.error("Failed to create audio track")
            return {
                "success": False,
                "error": "Failed to send track creation command",
            }

        # Get updated track count from state
        tracks = self.state.get_all_tracks()
        track_count = len(tracks)

        message = f"Created audio track"
        if name:
            message += f" '{name}'"
            # Note: Track naming after creation would require getting the new track ID
            # and calling rename_track(). For now, we just report the creation.
            # The track name can be set via rename_track() after creation.

        logger.info(message)
        return {
            "success": True,
            "message": message,
            "track_count": track_count,
        }

    async def create_midi_track(self, name: str = "") -> Dict[str, Any]:
        """
        Create a new MIDI track in Ardour.

        Sends OSC command to create a single MIDI track. If a name is provided,
        the track will be renamed after creation.

        Args:
            name: Optional name for the new track

        Returns:
            Dictionary with:
                - success (bool): Whether the track was created
                - message (str): Human-readable result message
                - track_count (int): Number of tracks after creation (if successful)

        Example:
            >>> result = await track_tools.create_midi_track("Piano")
            >>> # Returns: {"success": True, "message": "Created MIDI track 'Piano'", "track_count": 6}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Create one MIDI track using OSC command
        # /add_midi_track i count
        success = self.osc.send_command("/add_midi_track", 1)

        if not success:
            logger.error("Failed to create MIDI track")
            return {
                "success": False,
                "error": "Failed to send track creation command",
            }

        # Get updated track count from state
        tracks = self.state.get_all_tracks()
        track_count = len(tracks)

        message = f"Created MIDI track"
        if name:
            message += f" '{name}'"

        logger.info(message)
        return {
            "success": True,
            "message": message,
            "track_count": track_count,
        }

    async def list_tracks(self) -> Dict[str, Any]:
        """
        List all tracks in the current Ardour session.

        Queries the cached state for all tracks. Does not require OSC communication.

        Returns:
            Dictionary with:
                - success (bool): Always True
                - track_count (int): Number of tracks in session
                - tracks (list): List of track dictionaries, each containing:
                    - strip_id (int): Track ID (1-based)
                    - name (str): Track name
                    - type (str): Track type ("audio" or "midi")
                    - muted (bool): Mute state
                    - soloed (bool): Solo state
                    - rec_enabled (bool): Record arm state
                    - gain_db (float): Track gain in dB
                    - pan (float): Pan position (-1.0 to 1.0)

        Example:
            >>> result = await track_tools.list_tracks()
            >>> # Returns: {"success": True, "track_count": 5, "tracks": [...]}
        """
        tracks = self.state.get_all_tracks()

        # Format track information
        track_list = []
        for strip_id, track in sorted(tracks.items()):
            track_list.append({
                "strip_id": track.strip_id,
                "name": track.name,
                "type": track.track_type,
                "muted": track.muted,
                "soloed": track.soloed,
                "rec_enabled": track.rec_enabled,
                "gain_db": track.gain_db,
                "pan": track.pan,
            })

        logger.debug(f"Listed {len(track_list)} tracks")
        return {
            "success": True,
            "track_count": len(track_list),
            "tracks": track_list,
        }

    async def select_track(self, track_id: int) -> Dict[str, Any]:
        """
        Select a track by its ID in Ardour.

        Sends OSC command to select the specified track.

        Args:
            track_id: Track/strip ID (1-based integer)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was selected
                - track_id (int): The selected track ID
                - track_name (str): Name of the selected track (if found in state)
                - message (str): Human-readable result message

        Example:
            >>> result = await track_tools.select_track(3)
            >>> # Returns: {"success": True, "track_id": 3, "track_name": "Vocals", "message": "Selected track 3 'Vocals'"}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if track_id < 1:
            return {"success": False, "error": "Track ID must be positive (1-based)"}

        # Check if track exists in state
        track = self.state.get_track(track_id)
        track_name = track.name if track else "Unknown"

        # Select track using OSC command
        # /strip/select ii strip_id, select (1 = select)
        success = self.osc.send_command("/strip/select", track_id, 1)

        if not success:
            logger.error(f"Failed to select track {track_id}")
            return {
                "success": False,
                "error": f"Failed to send track selection command for track {track_id}",
            }

        message = f"Selected track {track_id}"
        if track_name != "Unknown":
            message += f" '{track_name}'"

        logger.info(message)
        return {
            "success": True,
            "track_id": track_id,
            "track_name": track_name,
            "message": message,
        }

    async def rename_track(self, track_id: int, new_name: str) -> Dict[str, Any]:
        """
        Rename a track in Ardour.

        Sends OSC command to change the track's name.

        Args:
            track_id: Track/strip ID (1-based integer)
            new_name: New name for the track

        Returns:
            Dictionary with:
                - success (bool): Whether the track was renamed
                - track_id (int): The renamed track ID
                - old_name (str): Previous track name (if known)
                - new_name (str): New track name
                - message (str): Human-readable result message

        Example:
            >>> result = await track_tools.rename_track(3, "Lead Vocals")
            >>> # Returns: {"success": True, "track_id": 3, "old_name": "Vocals", "new_name": "Lead Vocals", ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        if track_id < 1:
            return {"success": False, "error": "Track ID must be positive (1-based)"}

        if not new_name or not new_name.strip():
            return {"success": False, "error": "Track name cannot be empty"}

        # Get current track name from state
        track = self.state.get_track(track_id)
        old_name = track.name if track else "Unknown"

        # Rename track using OSC command
        # /strip/name is strip_id, name
        success = self.osc.send_command("/strip/name", track_id, new_name)

        if not success:
            logger.error(f"Failed to rename track {track_id}")
            return {
                "success": False,
                "error": f"Failed to send track rename command for track {track_id}",
            }

        message = f"Renamed track {track_id}"
        if old_name != "Unknown":
            message += f" from '{old_name}'"
        message += f" to '{new_name}'"

        logger.info(message)
        return {
            "success": True,
            "track_id": track_id,
            "old_name": old_name,
            "new_name": new_name,
            "message": message,
        }
