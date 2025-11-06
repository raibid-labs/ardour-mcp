"""
Main MCP server implementation for Ardour control.

This module sets up the MCP server and registers all available tools
for controlling Ardour via OSC.
"""

import asyncio
import logging
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server

from ardour_mcp.ardour_state import ArdourState
from ardour_mcp.osc_bridge import ArdourOSCBridge
from ardour_mcp.tools.mixer import MixerTools
from ardour_mcp.tools.navigation import NavigationTools
from ardour_mcp.tools.recording import RecordingTools
from ardour_mcp.tools.session import SessionTools
from ardour_mcp.tools.tracks import TrackTools
from ardour_mcp.tools.transport import TransportTools

logger = logging.getLogger(__name__)


class ArdourMCPServer:
    """
    Main MCP server for Ardour control.

    Manages the MCP server lifecycle, tool registration, and
    communication with Ardour via OSC.
    """

    def __init__(self, host: str = "localhost", port: int = 3819) -> None:
        """
        Initialize the Ardour MCP server.

        Args:
            host: Ardour OSC host address
            port: Ardour OSC port
        """
        self.host = host
        self.port = port

        # Initialize core components
        self.osc_bridge = ArdourOSCBridge(host, port)
        self.state = ArdourState()
        self.server = Server("ardour-mcp")

        # Initialize tool classes
        self.transport_tools = TransportTools(self.osc_bridge, self.state)
        self.track_tools = TrackTools(self.osc_bridge, self.state)
        self.session_tools = SessionTools(self.osc_bridge, self.state)
        self.mixer_tools = MixerTools(self.osc_bridge, self.state)
        self.navigation_tools = NavigationTools(self.osc_bridge, self.state)
        self.recording_tools = RecordingTools(self.osc_bridge, self.state)

        logger.info(f"Ardour MCP Server initialized for {host}:{port}")

    async def start(self) -> None:
        """
        Start the MCP server.

        This initializes the OSC connection, registers tools,
        and starts the MCP server.
        """
        logger.info("Starting Ardour MCP Server...")

        # Connect to Ardour OSC
        try:
            await self.osc_bridge.connect()
            logger.info("Connected to Ardour OSC")
        except Exception as e:
            logger.error(f"Failed to connect to Ardour: {e}")
            raise

        # Register state feedback handlers
        self.state.register_feedback_handlers(self.osc_bridge)
        logger.info("State feedback handlers registered")

        # Register MCP tools
        self._register_tools()

        logger.info("Ardour MCP Server started successfully")

    async def stop(self) -> None:
        """
        Stop the MCP server.

        Cleanly shuts down the OSC connection and MCP server.
        """
        logger.info("Stopping Ardour MCP Server...")

        # Disconnect from Ardour
        await self.osc_bridge.disconnect()

        # Clear state
        self.state.clear()

        logger.info("Ardour MCP Server stopped")

    def _register_tools(self) -> None:
        """
        Register all MCP tools.

        This method registers all available tools with the MCP server.
        Tools are organized by category:
        - Transport controls
        - Track management
        - Session information
        """
        # Transport Control Tools
        @self.server.call_tool()
        async def transport_play() -> list[Any]:
            """Start playback in Ardour."""
            result = await self.transport_tools.transport_play()
            return [result]

        @self.server.call_tool()
        async def transport_stop() -> list[Any]:
            """Stop playback in Ardour."""
            result = await self.transport_tools.transport_stop()
            return [result]

        @self.server.call_tool()
        async def transport_pause() -> list[Any]:
            """Toggle pause in Ardour."""
            result = await self.transport_tools.transport_pause()
            return [result]

        @self.server.call_tool()
        async def toggle_record() -> list[Any]:
            """Toggle recording mode in Ardour."""
            result = await self.transport_tools.toggle_record()
            return [result]

        @self.server.call_tool()
        async def goto_start() -> list[Any]:
            """Jump to session start."""
            result = await self.transport_tools.goto_start()
            return [result]

        @self.server.call_tool()
        async def goto_end() -> list[Any]:
            """Jump to session end."""
            result = await self.transport_tools.goto_end()
            return [result]

        @self.server.call_tool()
        async def goto_marker(marker_name: str) -> list[Any]:
            """
            Jump to a named marker.

            Args:
                marker_name: Name of the marker to jump to
            """
            result = await self.transport_tools.goto_marker(marker_name)
            return [result]

        @self.server.call_tool()
        async def locate(frame: int) -> list[Any]:
            """
            Jump to a specific frame position.

            Args:
                frame: Frame number to jump to
            """
            result = await self.transport_tools.locate(frame)
            return [result]

        @self.server.call_tool()
        async def set_loop_range(start_frame: int, end_frame: int) -> list[Any]:
            """
            Set loop range.

            Args:
                start_frame: Loop start frame
                end_frame: Loop end frame
            """
            result = await self.transport_tools.set_loop_range(start_frame, end_frame)
            return [result]

        @self.server.call_tool()
        async def toggle_loop() -> list[Any]:
            """Toggle loop mode."""
            result = await self.transport_tools.toggle_loop()
            return [result]

        @self.server.call_tool()
        async def get_transport_position() -> list[Any]:
            """Get current transport position and state."""
            result = await self.transport_tools.get_transport_position()
            return [result]

        # Track Management Tools
        @self.server.call_tool()
        async def create_audio_track(name: str = "") -> list[Any]:
            """
            Create a new audio track.

            Args:
                name: Optional name for the new track
            """
            result = await self.track_tools.create_audio_track(name)
            return [result]

        @self.server.call_tool()
        async def create_midi_track(name: str = "") -> list[Any]:
            """
            Create a new MIDI track.

            Args:
                name: Optional name for the new track
            """
            result = await self.track_tools.create_midi_track(name)
            return [result]

        @self.server.call_tool()
        async def list_tracks() -> list[Any]:
            """List all tracks in the session."""
            result = await self.track_tools.list_tracks()
            return [result]

        @self.server.call_tool()
        async def select_track(track_id: int) -> list[Any]:
            """
            Select a track by ID.

            Args:
                track_id: Track/strip ID (1-based)
            """
            result = await self.track_tools.select_track(track_id)
            return [result]

        @self.server.call_tool()
        async def rename_track(track_id: int, new_name: str) -> list[Any]:
            """
            Rename a track.

            Args:
                track_id: Track/strip ID (1-based)
                new_name: New name for the track
            """
            result = await self.track_tools.rename_track(track_id, new_name)
            return [result]

        # Session Information Tools
        @self.server.call_tool()
        async def get_session_info() -> list[Any]:
            """Get complete session information."""
            result = await self.session_tools.get_session_info()
            return [result]

        @self.server.call_tool()
        async def get_tempo() -> list[Any]:
            """Get current session tempo."""
            result = await self.session_tools.get_tempo()
            return [result]

        @self.server.call_tool()
        async def get_time_signature() -> list[Any]:
            """Get current time signature."""
            result = await self.session_tools.get_time_signature()
            return [result]

        @self.server.call_tool()
        async def get_sample_rate() -> list[Any]:
            """Get session sample rate."""
            result = await self.session_tools.get_sample_rate()
            return [result]

        @self.server.call_tool()
        async def list_markers() -> list[Any]:
            """List all markers in the session."""
            result = await self.session_tools.list_markers()
            return [result]

        @self.server.call_tool()
        async def save_session() -> list[Any]:
            """Save the current session."""
            result = await self.session_tools.save_session()
            return [result]

        @self.server.call_tool()
        async def get_track_count() -> list[Any]:
            """Get number of tracks in session."""
            result = await self.session_tools.get_track_count()
            return [result]

        @self.server.call_tool()
        async def is_session_dirty() -> list[Any]:
            """Check if session has unsaved changes."""
            result = await self.session_tools.is_session_dirty()
            return [result]

        # Mixer Control Tools
        @self.server.call_tool()
        async def set_track_volume(track_id: int, volume_db: float) -> list[Any]:
            """
            Set track volume/gain in dB.

            Args:
                track_id: Track/strip ID (1-based)
                volume_db: Gain in dB (range: -193.0 to +6.0)
            """
            result = await self.mixer_tools.set_track_volume(track_id, volume_db)
            return [result]

        @self.server.call_tool()
        async def set_track_pan(track_id: int, pan: float) -> list[Any]:
            """
            Set track pan position.

            Args:
                track_id: Track/strip ID (1-based)
                pan: Pan position (range: -1.0 to +1.0, where 0.0 = center)
            """
            result = await self.mixer_tools.set_track_pan(track_id, pan)
            return [result]

        @self.server.call_tool()
        async def set_track_mute(track_id: int, muted: bool) -> list[Any]:
            """
            Set track mute state.

            Args:
                track_id: Track/strip ID (1-based)
                muted: True to mute, False to unmute
            """
            result = await self.mixer_tools.set_track_mute(track_id, muted)
            return [result]

        @self.server.call_tool()
        async def toggle_track_mute(track_id: int) -> list[Any]:
            """
            Toggle track mute state.

            Args:
                track_id: Track/strip ID (1-based)
            """
            result = await self.mixer_tools.toggle_track_mute(track_id)
            return [result]

        @self.server.call_tool()
        async def set_track_solo(track_id: int, soloed: bool) -> list[Any]:
            """
            Set track solo state.

            Args:
                track_id: Track/strip ID (1-based)
                soloed: True to solo, False to unsolo
            """
            result = await self.mixer_tools.set_track_solo(track_id, soloed)
            return [result]

        @self.server.call_tool()
        async def toggle_track_solo(track_id: int) -> list[Any]:
            """
            Toggle track solo state.

            Args:
                track_id: Track/strip ID (1-based)
            """
            result = await self.mixer_tools.toggle_track_solo(track_id)
            return [result]

        @self.server.call_tool()
        async def set_track_rec_enable(track_id: int, enabled: bool) -> list[Any]:
            """
            Set track record enable state.

            Args:
                track_id: Track/strip ID (1-based)
                enabled: True to arm for recording, False to disarm
            """
            result = await self.mixer_tools.set_track_rec_enable(track_id, enabled)
            return [result]

        @self.server.call_tool()
        async def toggle_track_rec_enable(track_id: int) -> list[Any]:
            """
            Toggle track record enable state.

            Args:
                track_id: Track/strip ID (1-based)
            """
            result = await self.mixer_tools.toggle_track_rec_enable(track_id)
            return [result]

        @self.server.call_tool()
        async def arm_track_for_recording(track_id: int) -> list[Any]:
            """
            Arm a track for recording (convenience method).

            Args:
                track_id: Track/strip ID (1-based)
            """
            result = await self.mixer_tools.arm_track_for_recording(track_id)
            return [result]

        @self.server.call_tool()
        async def disarm_track(track_id: int) -> list[Any]:
            """
            Disarm a track from recording (convenience method).

            Args:
                track_id: Track/strip ID (1-based)
            """
            result = await self.mixer_tools.disarm_track(track_id)
            return [result]

        @self.server.call_tool()
        async def mute_all_tracks() -> list[Any]:
            """Mute all tracks in the session."""
            result = await self.mixer_tools.mute_all_tracks()
            return [result]

        @self.server.call_tool()
        async def unmute_all_tracks() -> list[Any]:
            """Unmute all tracks in the session."""
            result = await self.mixer_tools.unmute_all_tracks()
            return [result]

        @self.server.call_tool()
        async def clear_all_solos() -> list[Any]:
            """Clear solo state from all tracks."""
            result = await self.mixer_tools.clear_all_solos()
            return [result]

        @self.server.call_tool()
        async def get_track_mixer_state(track_id: int) -> list[Any]:
            """
            Get current mixer state for a track.

            Args:
                track_id: Track/strip ID (1-based)
            """
            result = await self.mixer_tools.get_track_mixer_state(track_id)
            return [result]

        # Navigation Control Tools - Marker Management
        @self.server.call_tool()
        async def create_marker(name: str, position: Optional[int] = None) -> list[Any]:
            """
            Create a marker at specified position or current position.

            Args:
                name: Name for the new marker
                position: Position in frames (None = current position)
            """
            result = await self.navigation_tools.create_marker(name, position)
            return [result]

        @self.server.call_tool()
        async def delete_marker(name: str) -> list[Any]:
            """
            Delete a marker by name.

            Args:
                name: Name of the marker to delete
            """
            result = await self.navigation_tools.delete_marker(name)
            return [result]

        @self.server.call_tool()
        async def rename_marker(old_name: str, new_name: str) -> list[Any]:
            """
            Rename a marker.

            Args:
                old_name: Current name of the marker
                new_name: New name for the marker
            """
            result = await self.navigation_tools.rename_marker(old_name, new_name)
            return [result]

        @self.server.call_tool()
        async def goto_marker_by_name(name: str) -> list[Any]:
            """
            Jump to a named marker.

            Args:
                name: Name of the marker to jump to
            """
            result = await self.navigation_tools.goto_marker(name)
            return [result]

        @self.server.call_tool()
        async def get_marker_position(name: str) -> list[Any]:
            """
            Get the position of a named marker.

            Args:
                name: Name of the marker to query
            """
            result = await self.navigation_tools.get_marker_position(name)
            return [result]

        # Navigation Control Tools - Loop Control
        @self.server.call_tool()
        async def set_loop_range_frames(start_frame: int, end_frame: int) -> list[Any]:
            """
            Set loop range in frames.

            Args:
                start_frame: Loop start position in frames
                end_frame: Loop end position in frames
            """
            result = await self.navigation_tools.set_loop_range(start_frame, end_frame)
            return [result]

        @self.server.call_tool()
        async def enable_loop() -> list[Any]:
            """Enable loop playback."""
            result = await self.navigation_tools.enable_loop()
            return [result]

        @self.server.call_tool()
        async def disable_loop() -> list[Any]:
            """Disable loop playback."""
            result = await self.navigation_tools.disable_loop()
            return [result]

        @self.server.call_tool()
        async def clear_loop_range() -> list[Any]:
            """Clear loop range and disable looping."""
            result = await self.navigation_tools.clear_loop_range()
            return [result]

        # Navigation Control Tools - Tempo & Time Signature
        @self.server.call_tool()
        async def set_session_tempo(bpm: float) -> list[Any]:
            """
            Set session tempo in beats per minute.

            Args:
                bpm: Tempo in BPM (range: 20.0 to 300.0)
            """
            result = await self.navigation_tools.set_tempo(bpm)
            return [result]

        @self.server.call_tool()
        async def get_session_tempo() -> list[Any]:
            """Get current session tempo."""
            result = await self.navigation_tools.get_tempo()
            return [result]

        @self.server.call_tool()
        async def set_session_time_signature(numerator: int, denominator: int) -> list[Any]:
            """
            Set time signature.

            Args:
                numerator: Beats per bar (e.g., 4 in 4/4 time)
                denominator: Note value per beat (e.g., 4 in 4/4 time)
            """
            result = await self.navigation_tools.set_time_signature(numerator, denominator)
            return [result]

        @self.server.call_tool()
        async def get_session_time_signature() -> list[Any]:
            """Get current time signature."""
            result = await self.navigation_tools.get_time_signature()
            return [result]

        # Navigation Control Tools - Navigation Helpers
        @self.server.call_tool()
        async def goto_timecode(hours: int, minutes: int, seconds: int, frames: int = 0) -> list[Any]:
            """
            Jump to a specific timecode position.

            Args:
                hours: Hours component (0-23)
                minutes: Minutes component (0-59)
                seconds: Seconds component (0-59)
                frames: Frame component (default: 0)
            """
            result = await self.navigation_tools.goto_time(hours, minutes, seconds, frames)
            return [result]

        @self.server.call_tool()
        async def goto_bar_number(bar_number: int) -> list[Any]:
            """
            Jump to a specific bar number.

            Args:
                bar_number: Bar number to jump to (1-based)
            """
            result = await self.navigation_tools.goto_bar(bar_number)
            return [result]

        @self.server.call_tool()
        async def skip_forward_seconds(seconds: float) -> list[Any]:
            """
            Skip forward by specified number of seconds.

            Args:
                seconds: Number of seconds to skip forward
            """
            result = await self.navigation_tools.skip_forward(seconds)
            return [result]

        @self.server.call_tool()
        async def skip_backward_seconds(seconds: float) -> list[Any]:
            """
            Skip backward by specified number of seconds.

            Args:
                seconds: Number of seconds to skip backward
            """
            result = await self.navigation_tools.skip_backward(seconds)
            return [result]

        # Recording Control Tools - Global Recording
        @self.server.call_tool()
        async def start_recording() -> list[Any]:
            """Start recording with transport playback."""
            result = await self.recording_tools.start_recording()
            return [result]

        @self.server.call_tool()
        async def stop_recording() -> list[Any]:
            """Stop recording and transport."""
            result = await self.recording_tools.stop_recording()
            return [result]

        @self.server.call_tool()
        async def toggle_recording() -> list[Any]:
            """Toggle global record enable state."""
            result = await self.recording_tools.toggle_recording()
            return [result]

        @self.server.call_tool()
        async def is_recording() -> list[Any]:
            """Query current recording state."""
            result = await self.recording_tools.is_recording()
            return [result]

        # Recording Control Tools - Punch Recording
        @self.server.call_tool()
        async def set_punch_range(start_frame: int, end_frame: int) -> list[Any]:
            """
            Set punch-in/out recording range.

            Args:
                start_frame: Punch-in point in frames
                end_frame: Punch-out point in frames
            """
            result = await self.recording_tools.set_punch_range(start_frame, end_frame)
            return [result]

        @self.server.call_tool()
        async def enable_punch_in() -> list[Any]:
            """Enable punch-in recording mode."""
            result = await self.recording_tools.enable_punch_in()
            return [result]

        @self.server.call_tool()
        async def enable_punch_out() -> list[Any]:
            """Enable punch-out recording mode."""
            result = await self.recording_tools.enable_punch_out()
            return [result]

        @self.server.call_tool()
        async def clear_punch_range() -> list[Any]:
            """Disable punch-in and punch-out modes."""
            result = await self.recording_tools.clear_punch_range()
            return [result]

        # Recording Control Tools - Input Monitoring
        @self.server.call_tool()
        async def set_input_monitoring(track_id: int, enabled: bool) -> list[Any]:
            """
            Enable/disable input monitoring for a track.

            Args:
                track_id: Track/strip ID (1-based)
                enabled: True to enable, False to disable
            """
            result = await self.recording_tools.set_input_monitoring(track_id, enabled)
            return [result]

        @self.server.call_tool()
        async def set_disk_monitoring(track_id: int, enabled: bool) -> list[Any]:
            """
            Enable/disable disk monitoring for a track.

            Args:
                track_id: Track/strip ID (1-based)
                enabled: True to enable, False to disable
            """
            result = await self.recording_tools.set_disk_monitoring(track_id, enabled)
            return [result]

        @self.server.call_tool()
        async def set_monitoring_mode(track_id: int, mode: str) -> list[Any]:
            """
            Set monitoring mode for a track.

            Args:
                track_id: Track/strip ID (1-based)
                mode: Monitoring mode ("input", "disk", or "auto")
            """
            result = await self.recording_tools.set_monitoring_mode(track_id, mode)
            return [result]

        # Recording Control Tools - Query Methods
        @self.server.call_tool()
        async def get_armed_tracks() -> list[Any]:
            """List all tracks armed for recording."""
            result = await self.recording_tools.get_armed_tracks()
            return [result]

        @self.server.call_tool()
        async def get_recording_state() -> list[Any]:
            """Get complete recording state."""
            result = await self.recording_tools.get_recording_state()
            return [result]

        logger.info("Registered 71 MCP tools (11 transport, 5 track, 9 session, 14 mixer, 17 navigation, 13 recording)")


async def serve() -> None:
    """
    Main async serve function for the MCP server.

    Initializes and runs the Ardour MCP server with stdio transport.
    """
    # Create server instance
    ardour_server = ArdourMCPServer()

    # Start the server (connects to Ardour and registers tools)
    await ardour_server.start()

    # Run the stdio server
    async with stdio_server() as (read_stream, write_stream):
        await ardour_server.server.run(
            read_stream,
            write_stream,
            ardour_server.server.create_initialization_options()
        )


def main() -> None:
    """
    Main entry point for the Ardour MCP server.

    Sets up logging and starts the server.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Ardour MCP - Model Context Protocol server for Ardour DAW")
    logger.info("Version: 0.0.1")

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
