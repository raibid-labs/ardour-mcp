"""
Tests for transport control tools.

Tests all transport-related MCP tools.
"""

from unittest.mock import Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, TransportState
from ardour_mcp.tools.transport import TransportTools


@pytest.fixture
def mock_osc_bridge():
    """Create a mock OSC bridge for testing."""
    bridge = Mock()
    bridge.is_connected.return_value = True
    bridge.send_command.return_value = True
    return bridge


@pytest.fixture
def mock_state():
    """Create a mock state with transport information."""
    state = Mock(spec=ArdourState)

    transport = TransportState(
        playing=False,
        recording=False,
        frame=0,
        tempo=120.0,
        time_signature=(4, 4),
        loop_enabled=False
    )

    state.get_transport.return_value = transport
    return state


@pytest.fixture
def transport_tools(mock_osc_bridge, mock_state):
    """Create TransportTools instance with mocked dependencies."""
    return TransportTools(mock_osc_bridge, mock_state)


class TestTransportToolsInitialization:
    """Test TransportTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of TransportTools."""
        tools = TransportTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state


class TestTransportPlay:
    """Test transport play functionality."""

    @pytest.mark.asyncio
    async def test_transport_play_success(self, transport_tools, mock_osc_bridge):
        """Test successfully starting playback."""
        result = await transport_tools.transport_play()

        mock_osc_bridge.send_command.assert_called_once_with("/transport_play")
        assert result["success"] is True
        assert "playing" in result
        assert "frame" in result

    @pytest.mark.asyncio
    async def test_transport_play_not_connected(self, transport_tools, mock_osc_bridge):
        """Test play when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await transport_tools.transport_play()

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_transport_play_command_fails(self, transport_tools, mock_osc_bridge):
        """Test handling play command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await transport_tools.transport_play()

        assert result["success"] is False


class TestTransportStop:
    """Test transport stop functionality."""

    @pytest.mark.asyncio
    async def test_transport_stop_success(self, transport_tools, mock_osc_bridge):
        """Test successfully stopping playback."""
        result = await transport_tools.transport_stop()

        mock_osc_bridge.send_command.assert_called_once_with("/transport_stop")
        assert result["success"] is True
        assert "playing" in result

    @pytest.mark.asyncio
    async def test_transport_stop_not_connected(self, transport_tools, mock_osc_bridge):
        """Test stop when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await transport_tools.transport_stop()

        assert result["success"] is False
        assert "Not connected" in result["error"]


class TestTransportPause:
    """Test transport pause functionality."""

    @pytest.mark.asyncio
    async def test_transport_pause_success(self, transport_tools, mock_osc_bridge):
        """Test successfully pausing/resuming."""
        result = await transport_tools.transport_pause()

        mock_osc_bridge.send_command.assert_called_once_with("/transport_pause")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_transport_pause_not_connected(self, transport_tools, mock_osc_bridge):
        """Test pause when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await transport_tools.transport_pause()

        assert result["success"] is False


class TestToggleRecord:
    """Test recording toggle functionality."""

    @pytest.mark.asyncio
    async def test_toggle_record_success(self, transport_tools, mock_osc_bridge):
        """Test successfully toggling recording."""
        result = await transport_tools.toggle_record()

        mock_osc_bridge.send_command.assert_called_once_with("/rec_enable_toggle")
        assert result["success"] is True
        assert "recording" in result

    @pytest.mark.asyncio
    async def test_toggle_record_not_connected(self, transport_tools, mock_osc_bridge):
        """Test toggle record when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await transport_tools.toggle_record()

        assert result["success"] is False


class TestNavigation:
    """Test navigation functionality."""

    @pytest.mark.asyncio
    async def test_goto_start_success(self, transport_tools, mock_osc_bridge):
        """Test jumping to session start."""
        result = await transport_tools.goto_start()

        mock_osc_bridge.send_command.assert_called_once_with("/goto_start")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_goto_end_success(self, transport_tools, mock_osc_bridge):
        """Test jumping to session end."""
        result = await transport_tools.goto_end()

        mock_osc_bridge.send_command.assert_called_once_with("/goto_end")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_goto_marker_success(self, transport_tools, mock_osc_bridge):
        """Test jumping to a named marker."""
        result = await transport_tools.goto_marker("Verse 1")

        mock_osc_bridge.send_command.assert_called_once_with("/locate", "Verse 1")
        assert result["success"] is True
        assert "Verse 1" in result["marker"]

    @pytest.mark.asyncio
    async def test_goto_marker_empty_name(self, transport_tools, mock_osc_bridge):
        """Test goto marker with empty name."""
        result = await transport_tools.goto_marker("")

        assert result["success"] is False
        assert "required" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_goto_marker_not_connected(self, transport_tools, mock_osc_bridge):
        """Test goto marker when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await transport_tools.goto_marker("Test")

        assert result["success"] is False


class TestLocate:
    """Test locate functionality."""

    @pytest.mark.asyncio
    async def test_locate_success(self, transport_tools, mock_osc_bridge):
        """Test locating to specific frame."""
        result = await transport_tools.locate(48000)

        mock_osc_bridge.send_command.assert_called_once_with("/locate", 48000)
        assert result["success"] is True
        assert "frame" in result

    @pytest.mark.asyncio
    async def test_locate_negative_frame(self, transport_tools, mock_osc_bridge):
        """Test locate with negative frame number."""
        result = await transport_tools.locate(-100)

        assert result["success"] is False
        assert "non-negative" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_locate_not_connected(self, transport_tools, mock_osc_bridge):
        """Test locate when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await transport_tools.locate(0)

        assert result["success"] is False


class TestLoopControl:
    """Test loop control functionality."""

    @pytest.mark.asyncio
    async def test_set_loop_range_success(self, transport_tools, mock_osc_bridge):
        """Test setting loop range."""
        result = await transport_tools.set_loop_range(0, 96000)

        mock_osc_bridge.send_command.assert_called_once_with("/set_loop_range", 0, 96000)
        assert result["success"] is True
        assert result["loop_start"] == 0
        assert result["loop_end"] == 96000

    @pytest.mark.asyncio
    async def test_set_loop_range_invalid_negative(self, transport_tools, mock_osc_bridge):
        """Test loop range with negative values."""
        result = await transport_tools.set_loop_range(-100, 1000)

        assert result["success"] is False
        assert "non-negative" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_loop_range_end_before_start(self, transport_tools, mock_osc_bridge):
        """Test loop range with end before start."""
        result = await transport_tools.set_loop_range(1000, 500)

        assert result["success"] is False
        assert "after start" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_toggle_loop_success(self, transport_tools, mock_osc_bridge):
        """Test toggling loop mode."""
        result = await transport_tools.toggle_loop()

        mock_osc_bridge.send_command.assert_called_once_with("/loop_toggle")
        assert result["success"] is True
        assert "loop_enabled" in result


class TestGetTransportPosition:
    """Test getting transport position."""

    @pytest.mark.asyncio
    async def test_get_transport_position_success(self, transport_tools, mock_state):
        """Test getting transport position."""
        result = await transport_tools.get_transport_position()

        assert result["success"] is True
        assert result["playing"] is False
        assert result["recording"] is False
        assert result["frame"] == 0
        assert result["tempo"] == 120.0
        assert result["time_signature"] == "4/4"
        assert result["loop_enabled"] is False


class TestSetTempo:
    """Test tempo control."""

    @pytest.mark.asyncio
    async def test_set_tempo_not_supported(self, transport_tools):
        """Test that set_tempo returns not supported message."""
        result = await transport_tools.set_tempo(140.0)

        assert result["success"] is False
        assert "not directly supported" in result["error"]

    @pytest.mark.asyncio
    async def test_set_tempo_invalid_range_low(self, transport_tools):
        """Test set_tempo with tempo too low."""
        result = await transport_tools.set_tempo(0)

        assert result["success"] is False
        assert "between 1 and 300" in result["error"]

    @pytest.mark.asyncio
    async def test_set_tempo_invalid_range_high(self, transport_tools):
        """Test set_tempo with tempo too high."""
        result = await transport_tools.set_tempo(350)

        assert result["success"] is False
        assert "between 1 and 300" in result["error"]


class TestTransportToolsIntegration:
    """Integration tests for transport tools."""

    @pytest.mark.asyncio
    async def test_play_stop_workflow(self, transport_tools, mock_osc_bridge):
        """Test play then stop workflow."""
        # Play
        play_result = await transport_tools.transport_play()
        assert play_result["success"] is True

        # Stop
        mock_osc_bridge.reset_mock()
        stop_result = await transport_tools.transport_stop()
        assert stop_result["success"] is True

    @pytest.mark.asyncio
    async def test_locate_and_play_workflow(self, transport_tools, mock_osc_bridge):
        """Test locate then play workflow."""
        # Locate
        locate_result = await transport_tools.locate(48000)
        assert locate_result["success"] is True

        # Play
        mock_osc_bridge.reset_mock()
        play_result = await transport_tools.transport_play()
        assert play_result["success"] is True

    @pytest.mark.asyncio
    async def test_loop_workflow(self, transport_tools, mock_osc_bridge):
        """Test setting loop range and enabling loop."""
        # Set loop range
        range_result = await transport_tools.set_loop_range(0, 96000)
        assert range_result["success"] is True

        # Enable loop
        mock_osc_bridge.reset_mock()
        loop_result = await transport_tools.toggle_loop()
        assert loop_result["success"] is True
