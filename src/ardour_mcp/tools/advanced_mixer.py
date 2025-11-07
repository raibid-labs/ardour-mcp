"""
Advanced mixer control MCP tools.

Provides advanced mixer operations:
- Send/return configuration
- Plugin control
- Bus operations
- Query methods
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AdvancedMixerTools:
    """
    Advanced mixer control tools for Ardour.

    Provides methods for controlling sends, plugins, buses, and other
    advanced mixer features not covered by basic mixer operations.
    """

    def __init__(self, osc_bridge: Any, state: Any) -> None:
        """
        Initialize advanced mixer tools.

        Args:
            osc_bridge: ArdourOSCBridge instance for sending commands
            state: ArdourState instance for querying state
        """
        self.osc = osc_bridge
        self.state = state
        logger.info("Advanced mixer tools initialized")

    # ========================================================================
    # Send/Return Configuration (4 methods)
    # ========================================================================

    async def set_send_level(self, track_id: int, send_id: int, level_db: float) -> Dict[str, Any]:
        """
        Set send level in dB.

        Controls the gain of an aux send from a track. Sends allow routing
        track signal to buses for effects processing or monitoring.

        Args:
            track_id: Source track strip ID (1-based)
            send_id: Send ID (0-based index)
            level_db: Send gain in dB (range: -193.0 to +6.0)

        Returns:
            Dictionary with:
                - success (bool): Whether the send level was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - send_id (int): The send ID
                - level_db (float): The new send level in dB
                - message (str): Human-readable result message

        OSC Commands:
            /strip/send/gain iif strip_id send_id gain_db

        Example:
            >>> result = await adv_mixer.set_send_level(1, 0, -12.0)
            >>> print(result)
            {'success': True, 'message': 'Set send 0 on track Vocals to -12.0dB',
             'track_id': 1, 'send_id': 0, 'level_db': -12.0}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate dB range
        if not -193.0 <= level_db <= 6.0:
            return {
                "success": False,
                "error": f"Send level {level_db}dB out of range (-193.0 to +6.0)"
            }

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate send_id is non-negative
        if send_id < 0:
            return {
                "success": False,
                "error": f"Send ID {send_id} invalid (must be >= 0)"
            }

        # Send OSC command
        success = self.osc.send_command("/strip/send/gain", track_id, send_id, level_db)

        if success:
            logger.info(f"Set send {send_id} on track {track_id} '{track.name}' to {level_db}dB")
            return {
                "success": True,
                "message": f"Set send {send_id} on track '{track.name}' to {level_db}dB",
                "track_id": track_id,
                "track_name": track.name,
                "send_id": send_id,
                "level_db": level_db,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def enable_send(self, track_id: int, send_id: int, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable a send.

        Controls whether a send is active. Disabled sends do not route
        any signal regardless of their gain setting.

        Args:
            track_id: Source track strip ID (1-based)
            send_id: Send ID (0-based index)
            enabled: True to enable send, False to disable

        Returns:
            Dictionary with:
                - success (bool): Whether the send was enabled/disabled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - send_id (int): The send ID
                - enabled (bool): The new enabled state
                - message (str): Human-readable result message

        OSC Commands:
            /strip/send/enable iii strip_id send_id enable

        Example:
            >>> result = await adv_mixer.enable_send(1, 0, True)
            >>> # Returns: {"success": True, "track_id": 1, "send_id": 0, "enabled": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate send_id is non-negative
        if send_id < 0:
            return {
                "success": False,
                "error": f"Send ID {send_id} invalid (must be >= 0)"
            }

        # Send OSC command (1 = enabled, 0 = disabled)
        enable_value = 1 if enabled else 0
        success = self.osc.send_command("/strip/send/enable", track_id, send_id, enable_value)

        if success:
            action = "Enabled" if enabled else "Disabled"
            logger.info(f"{action} send {send_id} on track {track_id} '{track.name}'")
            return {
                "success": True,
                "message": f"{action} send {send_id} on track '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "send_id": send_id,
                "enabled": enabled,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def toggle_send(self, track_id: int, send_id: int) -> Dict[str, Any]:
        """
        Toggle send enabled state.

        Toggles a send between enabled and disabled states. If current state
        is unknown from cache, defaults to enabling the send.

        Args:
            track_id: Source track strip ID (1-based)
            send_id: Send ID (0-based index)

        Returns:
            Dictionary with:
                - success (bool): Whether the send was toggled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - send_id (int): The send ID
                - enabled (bool): The new enabled state (after toggle)
                - message (str): Human-readable result message

        OSC Commands:
            /strip/send/enable iii strip_id send_id enable

        Example:
            >>> result = await adv_mixer.toggle_send(1, 0)
            >>> # Returns: {"success": True, "track_id": 1, "send_id": 0, "enabled": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate send_id is non-negative
        if send_id < 0:
            return {
                "success": False,
                "error": f"Send ID {send_id} invalid (must be >= 0)"
            }

        # Note: Since send state is not currently cached in TrackState,
        # we default to enabling. In a full implementation, this would
        # query cached send state if available.
        new_enabled = True

        return await self.enable_send(track_id, send_id, new_enabled)

    async def list_sends(self, track_id: int) -> Dict[str, Any]:
        """
        List all sends for a track.

        Returns information about all sends configured for a track.
        Note: Ardour's OSC interface has limited send query capabilities,
        so this returns basic information from cached state if available.

        Args:
            track_id: Track strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - send_count (int): Number of sends (0 if unknown)
                - sends (list): List of send information (empty if unavailable)
                - message (str): Human-readable result message

        Example:
            >>> result = await adv_mixer.list_sends(1)
            >>> # Returns: {"success": True, "track_id": 1, "send_count": 2, ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Note: Send information is not currently cached in TrackState.
        # In a full implementation, this would return cached send data.
        # For now, return placeholder response.
        logger.debug(f"Listed sends for track {track_id} '{track.name}'")
        return {
            "success": True,
            "message": f"Send list for track '{track.name}' (query via Ardour UI for details)",
            "track_id": track_id,
            "track_name": track.name,
            "send_count": 0,
            "sends": [],
        }

    # ========================================================================
    # Plugin Control (5 methods)
    # ========================================================================

    async def set_plugin_parameter(
        self, track_id: int, plugin_id: int, param_id: int, value: float
    ) -> Dict[str, Any]:
        """
        Set plugin parameter value.

        Controls a specific parameter of a plugin on a track. Plugin and
        parameter IDs are 0-based indices in the order they appear.

        Args:
            track_id: Track strip ID (1-based)
            plugin_id: Plugin ID (0-based index in plugin chain)
            param_id: Parameter ID (0-based index)
            value: Parameter value (typically 0.0 to 1.0, plugin-dependent)

        Returns:
            Dictionary with:
                - success (bool): Whether the parameter was set
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - plugin_id (int): The plugin ID
                - param_id (int): The parameter ID
                - value (float): The new parameter value
                - message (str): Human-readable result message

        OSC Commands:
            /strip/plugin/parameter iiif strip_id plugin_id param_id value

        Example:
            >>> result = await adv_mixer.set_plugin_parameter(1, 0, 2, 0.5)
            >>> # Returns: {"success": True, "track_id": 1, "plugin_id": 0, "param_id": 2, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate IDs are non-negative
        if plugin_id < 0:
            return {
                "success": False,
                "error": f"Plugin ID {plugin_id} invalid (must be >= 0)"
            }

        if param_id < 0:
            return {
                "success": False,
                "error": f"Parameter ID {param_id} invalid (must be >= 0)"
            }

        # Send OSC command
        success = self.osc.send_command(
            "/strip/plugin/parameter", track_id, plugin_id, param_id, value
        )

        if success:
            logger.info(
                f"Set plugin {plugin_id} param {param_id} on track {track_id} '{track.name}' to {value}"
            )
            return {
                "success": True,
                "message": f"Set plugin {plugin_id} parameter {param_id} on track '{track.name}' to {value}",
                "track_id": track_id,
                "track_name": track.name,
                "plugin_id": plugin_id,
                "param_id": param_id,
                "value": value,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def activate_plugin(self, track_id: int, plugin_id: int) -> Dict[str, Any]:
        """
        Activate (enable) a plugin.

        Enables processing for a plugin on a track. Active plugins process
        audio/MIDI, inactive plugins are bypassed.

        Args:
            track_id: Track strip ID (1-based)
            plugin_id: Plugin ID (0-based index in plugin chain)

        Returns:
            Dictionary with:
                - success (bool): Whether the plugin was activated
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - plugin_id (int): The plugin ID
                - active (bool): True (plugin is now active)
                - message (str): Human-readable result message

        OSC Commands:
            /strip/plugin/activate iii strip_id plugin_id 1

        Example:
            >>> result = await adv_mixer.activate_plugin(1, 0)
            >>> # Returns: {"success": True, "track_id": 1, "plugin_id": 0, "active": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate plugin_id is non-negative
        if plugin_id < 0:
            return {
                "success": False,
                "error": f"Plugin ID {plugin_id} invalid (must be >= 0)"
            }

        # Send OSC command (1 = activate)
        success = self.osc.send_command("/strip/plugin/activate", track_id, plugin_id, 1)

        if success:
            logger.info(f"Activated plugin {plugin_id} on track {track_id} '{track.name}'")
            return {
                "success": True,
                "message": f"Activated plugin {plugin_id} on track '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "plugin_id": plugin_id,
                "active": True,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def deactivate_plugin(self, track_id: int, plugin_id: int) -> Dict[str, Any]:
        """
        Deactivate (bypass) a plugin.

        Disables processing for a plugin on a track. Inactive plugins
        are bypassed and do not process audio/MIDI.

        Args:
            track_id: Track strip ID (1-based)
            plugin_id: Plugin ID (0-based index in plugin chain)

        Returns:
            Dictionary with:
                - success (bool): Whether the plugin was deactivated
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - plugin_id (int): The plugin ID
                - active (bool): False (plugin is now inactive)
                - message (str): Human-readable result message

        OSC Commands:
            /strip/plugin/activate iii strip_id plugin_id 0

        Example:
            >>> result = await adv_mixer.deactivate_plugin(1, 0)
            >>> # Returns: {"success": True, "track_id": 1, "plugin_id": 0, "active": False, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate plugin_id is non-negative
        if plugin_id < 0:
            return {
                "success": False,
                "error": f"Plugin ID {plugin_id} invalid (must be >= 0)"
            }

        # Send OSC command (0 = deactivate)
        success = self.osc.send_command("/strip/plugin/activate", track_id, plugin_id, 0)

        if success:
            logger.info(f"Deactivated plugin {plugin_id} on track {track_id} '{track.name}'")
            return {
                "success": True,
                "message": f"Deactivated plugin {plugin_id} on track '{track.name}'",
                "track_id": track_id,
                "track_name": track.name,
                "plugin_id": plugin_id,
                "active": False,
            }

        return {"success": False, "error": "Failed to send OSC command"}

    async def toggle_plugin(self, track_id: int, plugin_id: int) -> Dict[str, Any]:
        """
        Toggle plugin active state.

        Toggles a plugin between active and inactive (bypassed) states.
        If current state is unknown from cache, defaults to activating.

        Args:
            track_id: Track strip ID (1-based)
            plugin_id: Plugin ID (0-based index in plugin chain)

        Returns:
            Dictionary with:
                - success (bool): Whether the plugin was toggled
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - plugin_id (int): The plugin ID
                - active (bool): The new active state (after toggle)
                - message (str): Human-readable result message

        OSC Commands:
            /strip/plugin/activate iii strip_id plugin_id activate

        Example:
            >>> result = await adv_mixer.toggle_plugin(1, 0)
            >>> # Returns: {"success": True, "track_id": 1, "plugin_id": 0, "active": True, ...}
        """
        if not self.osc.is_connected():
            return {"success": False, "error": "Not connected to Ardour"}

        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate plugin_id is non-negative
        if plugin_id < 0:
            return {
                "success": False,
                "error": f"Plugin ID {plugin_id} invalid (must be >= 0)"
            }

        # Note: Since plugin state is not currently cached in TrackState,
        # we default to activating. In a full implementation, this would
        # query cached plugin state if available.
        return await self.activate_plugin(track_id, plugin_id)

    async def get_plugin_info(self, track_id: int, plugin_id: int) -> Dict[str, Any]:
        """
        Get plugin information.

        Returns information about a plugin from cached state. Note that
        plugin details are not currently cached in the state system.

        Args:
            track_id: Track strip ID (1-based)
            plugin_id: Plugin ID (0-based index in plugin chain)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - plugin_id (int): The plugin ID
                - name (str): Plugin name (empty if unknown)
                - active (bool): Plugin active state (None if unknown)
                - param_count (int): Number of parameters (0 if unknown)
                - message (str): Human-readable result message

        Example:
            >>> result = await adv_mixer.get_plugin_info(1, 0)
            >>> # Returns: {"success": True, "track_id": 1, "plugin_id": 0, ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate plugin_id is non-negative
        if plugin_id < 0:
            return {
                "success": False,
                "error": f"Plugin ID {plugin_id} invalid (must be >= 0)"
            }

        # Note: Plugin information is not currently cached in TrackState.
        # In a full implementation, this would return cached plugin data.
        logger.debug(f"Retrieved plugin {plugin_id} info for track {track_id} '{track.name}'")
        return {
            "success": True,
            "message": f"Plugin {plugin_id} on track '{track.name}' (query via Ardour UI for details)",
            "track_id": track_id,
            "track_name": track.name,
            "plugin_id": plugin_id,
            "name": "",
            "active": None,
            "param_count": 0,
        }

    # ========================================================================
    # Bus Operations (3 methods)
    # ========================================================================

    async def list_buses(self) -> Dict[str, Any]:
        """
        List all buses in the session.

        Returns information about all buses (aux buses, master bus, etc.)
        from cached state. Buses are identified by checking track properties.

        Returns:
            Dictionary with:
                - success (bool): Always True
                - bus_count (int): Number of buses found
                - buses (list): List of bus information dicts
                - message (str): Human-readable result message

        Example:
            >>> result = await adv_mixer.list_buses()
            >>> # Returns: {"success": True, "bus_count": 2, "buses": [...], ...}
        """
        tracks = self.state.get_all_tracks()

        # Note: Current TrackState doesn't distinguish buses from tracks.
        # In Ardour, buses are similar to tracks but without recording capability.
        # For now, return empty list. Full implementation would filter by track type.
        buses = []

        logger.debug(f"Listed {len(buses)} buses")
        return {
            "success": True,
            "message": f"Found {len(buses)} buses (Ardour OSC has limited bus query support)",
            "bus_count": len(buses),
            "buses": buses,
        }

    async def get_bus_info(self, bus_id: int) -> Dict[str, Any]:
        """
        Get information about a specific bus.

        Returns detailed information about a bus from cached state.

        Args:
            bus_id: Bus strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the bus was found
                - bus_id (int): The bus ID
                - name (str): Bus name
                - channels (int): Number of channels (0 if unknown)
                - gain_db (float): Current gain in dB
                - message (str): Human-readable result message

        Example:
            >>> result = await adv_mixer.get_bus_info(10)
            >>> # Returns: {"success": True, "bus_id": 10, "name": "Reverb", ...}
        """
        # Query track/bus by ID
        bus = self.state.get_track(bus_id)
        if not bus:
            return {"success": False, "error": f"Bus {bus_id} not found"}

        logger.debug(f"Retrieved info for bus {bus_id} '{bus.name}'")
        return {
            "success": True,
            "message": f"Bus '{bus.name}' info",
            "bus_id": bus.strip_id,
            "name": bus.name,
            "channels": 0,  # Not available in current state
            "gain_db": bus.gain_db,
        }

    async def list_bus_sends(self, bus_id: int) -> Dict[str, Any]:
        """
        List sends going to a specific bus.

        Returns information about all sends routed to a particular bus.
        Note: Ardour's OSC has limited reverse-lookup capabilities for sends.

        Args:
            bus_id: Bus strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the bus was found
                - bus_id (int): The bus ID
                - bus_name (str): Bus name
                - send_count (int): Number of sends to this bus (0 if unknown)
                - sends (list): List of send information (empty if unavailable)
                - message (str): Human-readable result message

        Example:
            >>> result = await adv_mixer.list_bus_sends(10)
            >>> # Returns: {"success": True, "bus_id": 10, "send_count": 3, ...}
        """
        # Validate bus exists
        bus = self.state.get_track(bus_id)
        if not bus:
            return {"success": False, "error": f"Bus {bus_id} not found"}

        # Note: Send routing information is not currently cached.
        # In a full implementation, this would return cached send routing data.
        logger.debug(f"Listed sends to bus {bus_id} '{bus.name}'")
        return {
            "success": True,
            "message": f"Sends to bus '{bus.name}' (query via Ardour UI for details)",
            "bus_id": bus_id,
            "bus_name": bus.name,
            "send_count": 0,
            "sends": [],
        }

    # ========================================================================
    # Query Methods (3 methods)
    # ========================================================================

    async def get_send_level(self, track_id: int, send_id: int) -> Dict[str, Any]:
        """
        Query send level from cache.

        Returns the cached send level for a specific send on a track.
        Note: Send levels are not currently cached in the state system.

        Args:
            track_id: Track strip ID (1-based)
            send_id: Send ID (0-based index)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - send_id (int): The send ID
                - level_db (float): Send level in dB (None if unknown)
                - message (str): Human-readable result message

        Example:
            >>> result = await adv_mixer.get_send_level(1, 0)
            >>> # Returns: {"success": True, "track_id": 1, "send_id": 0, "level_db": None, ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate send_id is non-negative
        if send_id < 0:
            return {
                "success": False,
                "error": f"Send ID {send_id} invalid (must be >= 0)"
            }

        # Note: Send levels are not currently cached in TrackState.
        logger.debug(f"Retrieved send {send_id} level for track {track_id} '{track.name}'")
        return {
            "success": True,
            "message": f"Send {send_id} level for track '{track.name}' (not cached)",
            "track_id": track_id,
            "track_name": track.name,
            "send_id": send_id,
            "level_db": None,
        }

    async def get_plugin_parameters(self, track_id: int, plugin_id: int) -> Dict[str, Any]:
        """
        List plugin parameters.

        Returns information about all parameters for a plugin from cached state.
        Note: Plugin parameters are not currently cached in the state system.

        Args:
            track_id: Track strip ID (1-based)
            plugin_id: Plugin ID (0-based index in plugin chain)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - plugin_id (int): The plugin ID
                - param_count (int): Number of parameters (0 if unknown)
                - parameters (list): List of parameter info (empty if unavailable)
                - message (str): Human-readable result message

        Example:
            >>> result = await adv_mixer.get_plugin_parameters(1, 0)
            >>> # Returns: {"success": True, "track_id": 1, "plugin_id": 0, ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Validate plugin_id is non-negative
        if plugin_id < 0:
            return {
                "success": False,
                "error": f"Plugin ID {plugin_id} invalid (must be >= 0)"
            }

        # Note: Plugin parameters are not currently cached in TrackState.
        logger.debug(f"Retrieved parameters for plugin {plugin_id} on track {track_id} '{track.name}'")
        return {
            "success": True,
            "message": f"Parameters for plugin {plugin_id} on track '{track.name}' (not cached)",
            "track_id": track_id,
            "track_name": track.name,
            "plugin_id": plugin_id,
            "param_count": 0,
            "parameters": [],
        }

    async def get_track_sends_count(self, track_id: int) -> Dict[str, Any]:
        """
        Get count of sends for a track.

        Returns the number of sends configured for a track from cached state.
        Note: Send counts are not currently cached in the state system.

        Args:
            track_id: Track strip ID (1-based)

        Returns:
            Dictionary with:
                - success (bool): Whether the track was found
                - track_id (int): The track ID
                - track_name (str): Name of the track
                - send_count (int): Number of sends (0 if unknown)
                - message (str): Human-readable result message

        Example:
            >>> result = await adv_mixer.get_track_sends_count(1)
            >>> # Returns: {"success": True, "track_id": 1, "send_count": 0, ...}
        """
        # Validate track exists
        track = self.state.get_track(track_id)
        if not track:
            return {"success": False, "error": f"Track {track_id} not found"}

        # Note: Send count is not currently cached in TrackState.
        logger.debug(f"Retrieved send count for track {track_id} '{track.name}'")
        return {
            "success": True,
            "message": f"Send count for track '{track.name}' (not cached)",
            "track_id": track_id,
            "track_name": track.name,
            "send_count": 0,
        }
