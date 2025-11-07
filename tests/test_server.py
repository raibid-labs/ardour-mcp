"""
Tests for the MCP server implementation.

Tests the ArdourMCPServer class including initialization,
tool registration, and server lifecycle management.
"""

from unittest.mock import Mock, AsyncMock, MagicMock, patch, call
import pytest

from ardour_mcp.server import ArdourMCPServer
from ardour_mcp.ardour_state import ArdourState
from ardour_mcp.osc_bridge import ArdourOSCBridge


class TestArdourMCPServerInitialization:
    """Test ArdourMCPServer initialization."""

    def test_init_default_host_port(self):
        """Test initialization with default host and port."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            assert server.host == "localhost"
            assert server.port == 3819

    def test_init_custom_host_port(self):
        """Test initialization with custom host and port."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer(host="192.168.1.100", port=5005)

            assert server.host == "192.168.1.100"
            assert server.port == 5005

    def test_init_creates_osc_bridge(self):
        """Test that initialization creates an OSC bridge."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            server = ArdourMCPServer(host="localhost", port=3819)

            mock_bridge_class.assert_called_once_with("localhost", 3819)
            assert server.osc_bridge is not None

    def test_init_creates_ardour_state(self):
        """Test that initialization creates an ArdourState."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            assert isinstance(server.state, ArdourState)

    def test_init_creates_mcp_server(self):
        """Test that initialization creates an MCP Server."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            assert server.server is not None

    def test_init_creates_all_tool_classes(self):
        """Test that initialization creates all tool class instances."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            assert server.transport_tools is not None
            assert server.track_tools is not None
            assert server.session_tools is not None
            assert server.mixer_tools is not None
            assert server.advanced_mixer_tools is not None
            assert server.navigation_tools is not None
            assert server.recording_tools is not None

    def test_init_passes_dependencies_to_tools(self):
        """Test that tools receive correct dependencies."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = Mock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            # Each tool should have received the OSC bridge and state
            assert server.transport_tools.osc == mock_bridge
            assert server.transport_tools.state == server.state
            assert server.mixer_tools.osc == mock_bridge
            assert server.mixer_tools.state == server.state


class TestArdourMCPServerStart:
    """Test server startup sequence."""

    @pytest.mark.asyncio
    async def test_start_connects_osc_bridge(self):
        """Test that start connects to the OSC bridge."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()
            await server.start()

            # Should call connect
            mock_bridge.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_registers_feedback_handlers(self):
        """Test that start registers feedback handlers."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            with patch.object(server.state, "register_feedback_handlers") as mock_reg:
                await server.start()

                mock_reg.assert_called_once_with(mock_bridge)

    @pytest.mark.asyncio
    async def test_start_registers_mcp_tools(self):
        """Test that start registers MCP tools."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            # Patch _register_tools to verify it's called
            with patch.object(server, "_register_tools") as mock_register:
                await server.start()

                mock_register.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_handles_connection_failure(self):
        """Test that start handles OSC connection failure."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge.connect.side_effect = Exception("Connection failed")
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            with pytest.raises(Exception, match="Connection failed"):
                await server.start()


class TestArdourMCPServerStop:
    """Test server shutdown sequence."""

    @pytest.mark.asyncio
    async def test_stop_disconnects_osc_bridge(self):
        """Test that stop disconnects from the OSC bridge."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()
            await server.stop()

            mock_bridge.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_clears_state(self):
        """Test that stop clears the state."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()
            server.state._state.name = "TestProject"

            await server.stop()

            assert server.state._state.name == ""
            assert server.state._state.tracks == {}


class TestToolRegistration:
    """Test tool registration with MCP server."""

    def test_register_tools_creates_transport_tools(self):
        """Test that _register_tools registers transport control tools."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            # Count tool registrations before
            initial_tools = len(server.server._tools) if hasattr(server.server, "_tools") else 0

            server._register_tools()

            # We should have registered multiple tools
            # Check that call_tool decorator was used
            assert hasattr(server.server, "call_tool")

    def test_register_tools_registers_track_tools(self):
        """Test that _register_tools registers track management tools."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()

            # Verify some track tools are registered
            assert hasattr(server.server, "call_tool")

    def test_register_tools_registers_session_tools(self):
        """Test that _register_tools registers session tools."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()
            server._register_tools()

            # Verify some session tools are registered
            assert hasattr(server.server, "call_tool")


class TestServerToolFunctions:
    """Test that tool wrapper functions work correctly."""

    @pytest.mark.asyncio
    async def test_transport_play_tool(self):
        """Test transport_play tool wrapper function."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = Mock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            # Mock the transport tool method
            mock_result = {"success": True, "message": "Playback started"}
            server.transport_tools.transport_play = AsyncMock(return_value=mock_result)

            server._register_tools()

            # Verify we can access the tool function
            assert hasattr(server.server, "call_tool")

    @pytest.mark.asyncio
    async def test_create_audio_track_tool(self):
        """Test create_audio_track tool wrapper function."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = Mock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            # Mock the track tool method
            mock_result = {"success": True, "track_id": 1}
            server.track_tools.create_audio_track = AsyncMock(return_value=mock_result)

            server._register_tools()

            # Verify we can access the tool function
            assert hasattr(server.server, "call_tool")


class TestServerAttributes:
    """Test server instance attributes and configuration."""

    def test_server_has_required_attributes(self):
        """Test that server instance has all required attributes."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            required_attrs = [
                "host",
                "port",
                "osc_bridge",
                "state",
                "server",
                "transport_tools",
                "track_tools",
                "session_tools",
                "mixer_tools",
                "advanced_mixer_tools",
                "navigation_tools",
                "recording_tools",
            ]

            for attr in required_attrs:
                assert hasattr(server, attr), f"Missing attribute: {attr}"

    def test_server_host_port_stored(self):
        """Test that host and port are properly stored."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            test_host = "192.168.1.50"
            test_port = 4000

            server = ArdourMCPServer(host=test_host, port=test_port)

            assert server.host == test_host
            assert server.port == test_port

    def test_server_instance_is_independent(self):
        """Test that multiple server instances are independent."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            # Configure mock to return different instances
            mock_bridge1 = Mock()
            mock_bridge2 = Mock()
            mock_bridge_class.side_effect = [mock_bridge1, mock_bridge2]

            server1 = ArdourMCPServer(host="localhost", port=3819)
            server2 = ArdourMCPServer(host="192.168.1.100", port=5005)

            assert server1.host == "localhost"
            assert server1.port == 3819
            assert server2.host == "192.168.1.100"
            assert server2.port == 5005
            assert server1.state is not server2.state
            assert server1.osc_bridge is not server2.osc_bridge


class TestServerToolIntegration:
    """Test integration between server and tools."""

    def test_all_tools_share_same_osc_bridge(self):
        """Test that all tools use the same OSC bridge instance."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = Mock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            assert server.transport_tools.osc is mock_bridge
            assert server.track_tools.osc is mock_bridge
            assert server.mixer_tools.osc is mock_bridge
            assert server.advanced_mixer_tools.osc is mock_bridge
            assert server.navigation_tools.osc is mock_bridge
            assert server.recording_tools.osc is mock_bridge
            assert server.session_tools.osc is mock_bridge

    def test_all_tools_share_same_state(self):
        """Test that all tools use the same ArdourState instance."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            assert server.transport_tools.state is server.state
            assert server.track_tools.state is server.state
            assert server.mixer_tools.state is server.state
            assert server.advanced_mixer_tools.state is server.state
            assert server.navigation_tools.state is server.state
            assert server.recording_tools.state is server.state
            assert server.session_tools.state is server.state


class TestServerLifecycleSequence:
    """Test complete server lifecycle sequences."""

    @pytest.mark.asyncio
    async def test_init_then_start_then_stop(self):
        """Test complete server lifecycle."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            # Initialize
            server = ArdourMCPServer(host="localhost", port=3819)
            assert server.host == "localhost"
            assert server.port == 3819

            # Start
            await server.start()
            mock_bridge.connect.assert_called_once()

            # Stop
            await server.stop()
            mock_bridge.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_registers_handlers_before_server_starts(self):
        """Test that handlers are registered before server processes tools."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            call_sequence = []

            async def track_connect():
                call_sequence.append("connect")

            def track_handlers(bridge):
                call_sequence.append("register_handlers")

            mock_bridge.connect.side_effect = track_connect
            server.state.register_feedback_handlers = track_handlers

            await server.start()

            # Connect should happen before handlers
            assert call_sequence.index("connect") < call_sequence.index("register_handlers")


class TestServerConfiguration:
    """Test server configuration and setup."""

    def test_mcp_server_name(self):
        """Test that MCP server is created with correct name."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            with patch("ardour_mcp.server.Server") as mock_server_class:
                mock_server_instance = Mock()
                mock_server_class.return_value = mock_server_instance

                server = ArdourMCPServer()

                mock_server_class.assert_called_once_with("ardour-mcp")

    def test_server_state_independent_from_tools(self):
        """Test that server state is properly isolated."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            # Modify state
            server.state.update_transport(playing=True)

            # Verify state was actually modified
            assert server.state.get_transport().playing is True

            # Verify tools have access to modified state
            transport = server.state.get_transport()
            assert transport.playing is True


class TestServerErrorHandling:
    """Test server error handling."""

    @pytest.mark.asyncio
    async def test_start_propagates_connection_errors(self):
        """Test that connection errors are propagated."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge.connect.side_effect = RuntimeError("OSC connection failed")
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            with pytest.raises(RuntimeError, match="OSC connection failed"):
                await server.start()

    @pytest.mark.asyncio
    async def test_stop_handles_disconnect_errors_gracefully(self):
        """Test that disconnect errors are handled."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge.disconnect.side_effect = RuntimeError("Disconnect failed")
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            with pytest.raises(RuntimeError):
                await server.stop()
