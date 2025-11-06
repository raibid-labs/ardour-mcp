"""
Mixer control MCP tools.

Provides tools for mixer operations:
- Volume/gain control
- Pan control
- Mute/solo/rec enable
- Batch operations
- Mixer state queries
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class MixerTools:
    """
    Mixer control tools for Ardour.

    Provides methods for controlling track mixer parameters including
    volume, pan, mute, solo, and recording arm states.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize mixer tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state
        logger.info("Mixer tools initialized")

    async def set_track_volume(self, track_id: int, volume_db: float) -> Dict[str, Any]:
        """
        Set track volume/gain in dB.

        Sends OSC command to set the track's gain fader position.
        The gain range matches Ardour's fader range from -193dB (silent)
        to +6dB (maximum boost).

        Args:
            track_id: Strip ID of the track (1-based integer)
            volume_db: Gain in dB (range: -193.0 to +6.0)

        Returns:
            Dictionary with:
                - success (bool): Whether the volume was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - volume_db (float): The new volume in dB
                - message (str): Human-readable result message

        OSC Commands:
            /strip/gain if strip_id gain_db

        Example:
            >>> result = await mixer_tools.set_track_volume(1, -6.0)
            >>> # Returns: {"success": True, "track_id": 1, "track_name": "Vocals", "volume_db": -6.0, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate range (-193dB to +6dB is Ardour's standard range)
        if not -193.0 <= volume_db <= 6.0:
            return {
                "success": False,
                "error": f"Volume {volume_db}dB out of range (-193.0 to +6.0)",
            }

        # Check track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Send OSC command
        success = self.osc.send_command("/strip/gain", track_id, volume_db)

        if success:
            logger.info(f"Set volume for track {track_id} '{track.name}' to {volume_db}dB")
            return {
                "success": True,
                "message": f"Set volume for track '{track.name}' to {volume_db}dB",
                "track_id": track_id,
                "track_name": track.name,
                "volume_db": volume_db,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def set_track_pan(self, track_id: int, pan: float) -> Dict[str, Any]:
        """
        Set track pan position.

        Sends OSC command to set the track's stereo pan position.
        Pan values range from -1.0 (hard left) through 0.0 (center)
        to +1.0 (hard right).

        Args:
            track_id: Strip ID of the track (1-based integer)
            pan: Pan position (range: -1.0 to +1.0, where 0.0 = center)

        Returns:
            Dictionary with:
                - success (bool): Whether the pan was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - pan (float): The new pan position
                - message (str): Human-readable result message

        OSC Commands:
            /strip/pan_stereo_position if strip_id position

        Example:
            >>> result = await mixer_tools.set_track_pan(1, -0.5)
            >>> # Returns: {"success": True, "track_id": 1, "pan": -0.5, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate range
        if not -1.0 <= pan <= 1.0:
            return {
                "success": False,
                "error": f"Pan {pan} out of range (-1.0 to +1.0)",
            }

        # Check track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Send OSC command
        success = self.osc.send_command("/strip/pan_stereo_position", track_id, pan)

        if success:
            # Format pan position for display
            if pan < -0.01:
                pan_desc = f"{abs(pan)*100:.0f}% left"
            elif pan > 0.01:
                pan_desc = f"{pan*100:.0f}% right"
            else:
                pan_desc = "center"

            logger.info(f"Set pan for track {track_id} '{track.name}' to {pan_desc}")
            return {
                "success": True,
                "message": f"Set pan for track '{track.name}' to {pan_desc}",
                "track_id": track_id,
                "track_name": track.name,
                "pan": pan,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def set_track_mute(self, track_id: int, muted: bool) -> Dict[str, Any]:
        """
        Set track mute state.

        Sends OSC command to mute or unmute a track.
        Muted tracks do not output audio.

        Args:
            track_id: Strip ID of the track (1-based integer)
            muted: True to mute, False to unmute

        Returns:
            Dictionary with:
                - success (bool): Whether the mute state was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - muted (bool): The new mute state
                - message (str): Human-readable result message

        OSC Commands:
            /strip/mute if strip_id mute (1 = muted, 0 = unmuted)

        Example:
            >>> result = await mixer_tools.set_track_mute(1, True)
            >>> # Returns: {"success": True, "track_id": 1, "muted": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Send OSC command (1 = muted, 0 = unmuted)
        mute_value = 1 if muted else 0
        success = self.osc.send_command("/strip/mute", track_id, mute_value)

        if success:
            action = "Muted" if muted else "Unmuted"
            logger.info(f"{action} track {track_id} '{track.name}'")
            return {
                "success": True,
                "message": f"{action} track '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "muted": muted,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def toggle_track_mute(self, track_id: int) -> Dict[str, Any]:
        """
        Toggle track mute state.

        Queries the current mute state from cached state and toggles it.
        If track is muted, it will be unmuted, and vice versa.

        Args:
            track_id: Strip ID of the track (1-based integer)

        Returns:
            Dictionary with:
                - success (bool): Whether the mute state was toggled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - muted (bool): The new mute state (after toggle)
                - message (str): Human-readable result message

        OSC Commands:
            /strip/mute if strip_id mute

        Example:
            >>> result = await mixer_tools.toggle_track_mute(1)
            >>> # Returns: {"success": True, "track_id": 1, "muted": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check track exists and get current state
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Toggle the mute state
        new_muted = not track.muted
        return await self.set_track_mute(track_id, new_muted)

    async def set_track_solo(self, track_id: int, soloed: bool) -> Dict[str, Any]:
        """
        Set track solo state.

        Sends OSC command to solo or unsolo a track.
        When a track is soloed, only soloed tracks are heard.

        Args:
            track_id: Strip ID of the track (1-based integer)
            soloed: True to solo, False to unsolo

        Returns:
            Dictionary with:
                - success (bool): Whether the solo state was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - soloed (bool): The new solo state
                - message (str): Human-readable result message

        OSC Commands:
            /strip/solo if strip_id solo (1 = soloed, 0 = unsoloed)

        Example:
            >>> result = await mixer_tools.set_track_solo(1, True)
            >>> # Returns: {"success": True, "track_id": 1, "soloed": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Send OSC command (1 = soloed, 0 = unsoloed)
        solo_value = 1 if soloed else 0
        success = self.osc.send_command("/strip/solo", track_id, solo_value)

        if success:
            action = "Soloed" if soloed else "Unsoloed"
            logger.info(f"{action} track {track_id} '{track.name}'")
            return {
                "success": True,
                "message": f"{action} track '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "soloed": soloed,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def toggle_track_solo(self, track_id: int) -> Dict[str, Any]:
        """
        Toggle track solo state.

        Queries the current solo state from cached state and toggles it.
        If track is soloed, it will be unsoloed, and vice versa.

        Args:
            track_id: Strip ID of the track (1-based integer)

        Returns:
            Dictionary with:
                - success (bool): Whether the solo state was toggled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - soloed (bool): The new solo state (after toggle)
                - message (str): Human-readable result message

        OSC Commands:
            /strip/solo if strip_id solo

        Example:
            >>> result = await mixer_tools.toggle_track_solo(1)
            >>> # Returns: {"success": True, "track_id": 1, "soloed": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check track exists and get current state
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Toggle the solo state
        new_soloed = not track.soloed
        return await self.set_track_solo(track_id, new_soloed)

    async def set_track_rec_enable(self, track_id: int, enabled: bool) -> Dict[str, Any]:
        """
        Set track record enable state.

        Sends OSC command to arm or disarm a track for recording.
        When armed, the track will record incoming audio/MIDI when
        global recording is enabled.

        Args:
            track_id: Strip ID of the track (1-based integer)
            enabled: True to arm for recording, False to disarm

        Returns:
            Dictionary with:
                - success (bool): Whether the rec enable state was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - rec_enabled (bool): The new record enable state
                - message (str): Human-readable result message

        OSC Commands:
            /strip/recenable if strip_id enable (1 = armed, 0 = disarmed)

        Example:
            >>> result = await mixer_tools.set_track_rec_enable(1, True)
            >>> # Returns: {"success": True, "track_id": 1, "rec_enabled": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Send OSC command (1 = armed, 0 = disarmed)
        rec_value = 1 if enabled else 0
        success = self.osc.send_command("/strip/recenable", track_id, rec_value)

        if success:
            action = "Armed" if enabled else "Disarmed"
            logger.info(f"{action} track {track_id} '{track.name}' for recording")
            return {
                "success": True,
                "message": f"{action} track '{track.name}' for recording",
                "track_id": track_id,
                "track_name": track.name,
                "rec_enabled": enabled,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def toggle_track_rec_enable(self, track_id: int) -> Dict[str, Any]:
        """
        Toggle track record enable state.

        Queries the current record enable state from cached state and toggles it.
        If track is armed, it will be disarmed, and vice versa.

        Args:
            track_id: Strip ID of the track (1-based integer)

        Returns:
            Dictionary with:
                - success (bool): Whether the rec enable state was toggled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - rec_enabled (bool): The new rec enable state (after toggle)
                - message (str): Human-readable result message

        OSC Commands:
            /strip/recenable if strip_id enable

        Example:
            >>> result = await mixer_tools.toggle_track_rec_enable(1)
            >>> # Returns: {"success": True, "track_id": 1, "rec_enabled": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Check track exists and get current state
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Toggle the rec enable state
        new_enabled = not track.rec_enabled
        return await self.set_track_rec_enable(track_id, new_enabled)

    async def arm_track_for_recording(self, track_id: int) -> Dict[str, Any]:
        """
        Arm a track for recording.

        Convenience method that arms the specified track for recording.
        Equivalent to calling set_track_rec_enable(track_id, True).

        Args:
            track_id: Strip ID of the track (1-based integer)

        Returns:
            Dictionary with success status and track info

        OSC Commands:
            /strip/recenable if strip_id 1

        Example:
            >>> result = await mixer_tools.arm_track_for_recording(1)
            >>> # Returns: {"success": True, "track_id": 1, "rec_enabled": True, ...}
        """
        return await self.set_track_rec_enable(track_id, True)

    async def disarm_track(self, track_id: int) -> Dict[str, Any]:
        """
        Disarm a track from recording.

        Convenience method that disarms the specified track from recording.
        Equivalent to calling set_track_rec_enable(track_id, False).

        Args:
            track_id: Strip ID of the track (1-based integer)

        Returns:
            Dictionary with success status and track info

        OSC Commands:
            /strip/recenable if strip_id 0

        Example:
            >>> result = await mixer_tools.disarm_track(1)
            >>> # Returns: {"success": True, "track_id": 1, "rec_enabled": False, ...}
        """
        return await self.set_track_rec_enable(track_id, False)

    async def mute_all_tracks(self) -> Dict[str, Any]:
        """
        Mute all tracks in the session.

        Queries all tracks from the state and sends mute commands for each.
        Returns summary of the operation including number of tracks muted.

        Returns:
            Dictionary with:
                - success (bool): Whether all tracks were muted successfully
                - tracks_muted (int): Number of tracks that were muted
                - total_tracks (int): Total number of tracks in session
                - message (str): Human-readable result message
                - failed_tracks (list): List of track IDs that failed (if any)

        OSC Commands:
            /strip/mute if strip_id 1 (for each track)

        Example:
            >>> result = await mixer_tools.mute_all_tracks()
            >>> # Returns: {"success": True, "tracks_muted": 5, "total_tracks": 5, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        tracks = self.state.get_all_tracks()
        total_tracks = len(tracks)

        if total_tracks == 0:
            return {
                "success": True,
                "message": "No tracks to mute",
                "tracks_muted": 0,
                "total_tracks": 0,
            }

        failed_tracks = []
        muted_count = 0

        for track_id in tracks.keys():
            result = await self.set_track_mute(track_id, True)
            if result["success"]:
                muted_count += 1
            else:
                failed_tracks.append(track_id)

        success = len(failed_tracks) == 0
        logger.info(f"Muted {muted_count}/{total_tracks} tracks")

        response = {
            "success": success,
            "message": f"Muted {muted_count}/{total_tracks} tracks",
            "tracks_muted": muted_count,
            "total_tracks": total_tracks,
        }

        if failed_tracks:
            response["failed_tracks"] = failed_tracks

        return response

    async def unmute_all_tracks(self) -> Dict[str, Any]:
        """
        Unmute all tracks in the session.

        Queries all tracks from the state and sends unmute commands for each.
        Returns summary of the operation including number of tracks unmuted.

        Returns:
            Dictionary with:
                - success (bool): Whether all tracks were unmuted successfully
                - tracks_unmuted (int): Number of tracks that were unmuted
                - total_tracks (int): Total number of tracks in session
                - message (str): Human-readable result message
                - failed_tracks (list): List of track IDs that failed (if any)

        OSC Commands:
            /strip/mute if strip_id 0 (for each track)

        Example:
            >>> result = await mixer_tools.unmute_all_tracks()
            >>> # Returns: {"success": True, "tracks_unmuted": 5, "total_tracks": 5, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        tracks = self.state.get_all_tracks()
        total_tracks = len(tracks)

        if total_tracks == 0:
            return {
                "success": True,
                "message": "No tracks to unmute",
                "tracks_unmuted": 0,
                "total_tracks": 0,
            }

        failed_tracks = []
        unmuted_count = 0

        for track_id in tracks.keys():
            result = await self.set_track_mute(track_id, False)
            if result["success"]:
                unmuted_count += 1
            else:
                failed_tracks.append(track_id)

        success = len(failed_tracks) == 0
        logger.info(f"Unmuted {unmuted_count}/{total_tracks} tracks")

        response = {
            "success": success,
            "message": f"Unmuted {unmuted_count}/{total_tracks} tracks",
            "tracks_unmuted": unmuted_count,
            "total_tracks": total_tracks,
        }

        if failed_tracks:
            response["failed_tracks"] = failed_tracks

        return response

    async def clear_all_solos(self) -> Dict[str, Any]:
        """
        Clear solo state from all tracks.

        Queries all tracks from the state and sends unsolo commands for each.
        This is useful to quickly return to normal monitoring after soloing.

        Returns:
            Dictionary with:
                - success (bool): Whether all tracks were unsoloed successfully
                - tracks_unsoloed (int): Number of tracks that were unsoloed
                - total_tracks (int): Total number of tracks in session
                - message (str): Human-readable result message
                - failed_tracks (list): List of track IDs that failed (if any)

        OSC Commands:
            /strip/solo if strip_id 0 (for each track)

        Example:
            >>> result = await mixer_tools.clear_all_solos()
            >>> # Returns: {"success": True, "tracks_unsoloed": 5, "total_tracks": 5, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        tracks = self.state.get_all_tracks()
        total_tracks = len(tracks)

        if total_tracks == 0:
            return {
                "success": True,
                "message": "No tracks to unsolo",
                "tracks_unsoloed": 0,
                "total_tracks": 0,
            }

        failed_tracks = []
        unsoloed_count = 0

        for track_id in tracks.keys():
            result = await self.set_track_solo(track_id, False)
            if result["success"]:
                unsoloed_count += 1
            else:
                failed_tracks.append(track_id)

        success = len(failed_tracks) == 0
        logger.info(f"Cleared solo on {unsoloed_count}/{total_tracks} tracks")

        response = {
            "success": success,
            "message": f"Cleared solo on {unsoloed_count}/{total_tracks} tracks",
            "tracks_unsoloed": unsoloed_count,
            "total_tracks": total_tracks,
        }

        if failed_tracks:
            response["failed_tracks"] = failed_tracks

        return response

    async def get_track_mixer_state(self, track_id: int) -> Dict[str, Any]:
        """
        Get current mixer state for a track.

        Queries the cached state for the track's mixer parameters.
        Does not require OSC communication - returns cached values.

        Args:
            track_id: Strip ID of the track (1-based integer)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - gain_db (float): Current gain in dB
                - pan (float): Current pan position (-1.0 to 1.0)
                - muted (bool): Current mute state
                - soloed (bool): Current solo state
                - rec_enabled (bool): Current record enable state
                - track_type (str): Track type ("audio" or "midi")

        Example:
            >>> result = await mixer_tools.get_track_mixer_state(1)
            >>> # Returns: {"success": True, "track_id": 1, "track_name": "Vocals",
            >>> #           "gain_db": -6.0, "pan": 0.0, "muted": False, ...}
        """
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        logger.debug(f"Retrieved mixer state for track {track_id} '{track.name}'")
        return {
            "success": True,
            "track_id": track.strip_id,
            "track_name": track.name,
            "track_type": track.track_type,
            "gain_db": track.gain_db,
            "pan": track.pan,
            "muted": track.muted,
            "soloed": track.soloed,
            "rec_enabled": track.rec_enabled,
        }
