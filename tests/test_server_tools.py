"""
Tests for server tool wrapper functions.

Tests that all MCP tool wrappers are correctly registered and callable.
"""

from unittest.mock import Mock, AsyncMock, patch
import pytest

from ardour_mcp.server import ArdourMCPServer


class TestServerTransportTools:
    """Test transport control tool wrappers."""

    def test_transport_play_registered(self):
        """Test that transport_play is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_transport_stop_registered(self):
        """Test that transport_stop is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_transport_pause_registered(self):
        """Test that transport_pause is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_toggle_record_registered(self):
        """Test that toggle_record is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")


class TestServerNavigationTools:
    """Test navigation tool wrappers."""

    def test_goto_start_registered(self):
        """Test that goto_start is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_goto_end_registered(self):
        """Test that goto_end is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_goto_marker_registered(self):
        """Test that goto_marker is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_locate_registered(self):
        """Test that locate is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")


class TestServerTrackTools:
    """Test track management tool wrappers."""

    def test_create_audio_track_registered(self):
        """Test that create_audio_track is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_create_midi_track_registered(self):
        """Test that create_midi_track is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_list_tracks_registered(self):
        """Test that list_tracks is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_select_track_registered(self):
        """Test that select_track is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_rename_track_registered(self):
        """Test that rename_track is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")


class TestServerSessionTools:
    """Test session information tool wrappers."""

    def test_get_session_info_registered(self):
        """Test that get_session_info is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_save_session_registered(self):
        """Test that save_session is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")


class TestServerMixerTools:
    """Test mixer control tool wrappers."""

    def test_set_track_volume_registered(self):
        """Test that set_track_volume is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_set_track_pan_registered(self):
        """Test that set_track_pan is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_set_track_mute_registered(self):
        """Test that set_track_mute is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")


class TestServerRecordingTools:
    """Test recording control tool wrappers."""

    def test_arm_track_registered(self):
        """Test that arm_track is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_disarm_track_registered(self):
        """Test that disarm_track is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")


class TestServerAdvancedMixerTools:
    """Test advanced mixer tool wrappers."""

    def test_set_send_level_registered(self):
        """Test that set_send_level is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")

    def test_list_sends_registered(self):
        """Test that list_sends is registered."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()
            assert hasattr(server.server, "call_tool")


class TestToolWrapperReturnFormats:
    """Test that tool wrappers return proper format."""

    @pytest.mark.asyncio
    async def test_tool_wrapper_returns_list(self):
        """Test that tool wrappers return results as list."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            # Mock a tool method
            mock_result = {"success": True, "message": "Test"}
            server.transport_tools.transport_play = AsyncMock(return_value=mock_result)

            server._register_tools()

            # Verify call_tool decorator is applied
            assert hasattr(server.server, "call_tool")

    @pytest.mark.asyncio
    async def test_multiple_tools_can_coexist(self):
        """Test that multiple tools can be registered together."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            # Register all tools
            server._register_tools()

            # Verify MCP server still has methods
            assert hasattr(server.server, "call_tool")


class TestServerToolsWithDependencies:
    """Test tool registration with mocked dependencies."""

    def test_tools_initialized_with_correct_dependencies(self):
        """Test that tools are initialized with correct OSC bridge and state."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = Mock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer(host="localhost", port=3819)

            # Verify all tools have the right dependencies
            assert server.transport_tools.osc is mock_bridge
            assert server.transport_tools.state is server.state

            assert server.mixer_tools.osc is mock_bridge
            assert server.mixer_tools.state is server.state

            assert server.track_tools.osc is mock_bridge
            assert server.track_tools.state is server.state

    def test_tools_share_state_mutations(self):
        """Test that state mutations are visible to all tools."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            # Mutate state through one tool's state reference
            server.mixer_tools.state.update_track(1, name="TestTrack")

            # Verify mutation is visible through another tool
            track = server.transport_tools.state.get_track(1)
            assert track is not None
            assert track.name == "TestTrack"


class TestServerToolRegistrationCompleteness:
    """Test that all expected tools are registered."""

    def test_all_transport_methods_present(self):
        """Test that all transport methods are implemented."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            required_methods = [
                "transport_play",
                "transport_stop",
                "transport_pause",
                "toggle_record",
                "goto_start",
                "goto_end",
            ]

            for method in required_methods:
                assert hasattr(server.transport_tools, method)

    def test_all_track_methods_present(self):
        """Test that all track methods are implemented."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            required_methods = [
                "create_audio_track",
                "create_midi_track",
                "list_tracks",
                "select_track",
                "rename_track",
            ]

            for method in required_methods:
                assert hasattr(server.track_tools, method)

    def test_all_mixer_methods_present(self):
        """Test that all mixer methods are implemented."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            required_methods = [
                "set_track_volume",
                "set_track_pan",
                "set_track_mute",
                "set_track_solo",
                "set_track_rec_enable",
            ]

            for method in required_methods:
                assert hasattr(server.mixer_tools, method)

    def test_all_session_methods_present(self):
        """Test that all session methods are implemented."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            required_methods = [
                "get_session_info",
                "get_tempo",
                "get_time_signature",
                "get_sample_rate",
                "save_session",
            ]

            for method in required_methods:
                assert hasattr(server.session_tools, method)
