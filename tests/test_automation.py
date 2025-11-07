"""
Tests for automation control tools.

Tests all automation-related MCP tools including automation modes,
recording, editing, and playback control.
"""

from unittest.mock import Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, TrackState
from ardour_mcp.tools.automation import AutomationTools


@pytest.fixture
def mock_osc_bridge():
    """Create a mock OSC bridge for testing."""
    bridge = Mock()
    bridge.is_connected.return_value = True
    bridge.send_command.return_value = True
    return bridge


@pytest.fixture
def mock_state():
    """Create a mock state with sample tracks."""
    state = Mock(spec=ArdourState)

    # Create sample tracks
    tracks = {
        1: TrackState(
            strip_id=1,
            name="Vocals",
            track_type="audio",
            gain_db=-6.0,
            pan=0.0,
            muted=False,
            soloed=False,
            rec_enabled=False,
        ),
        2: TrackState(
            strip_id=2,
            name="Guitar",
            track_type="audio",
            gain_db=-3.0,
            pan=-0.5,
            muted=False,
            soloed=False,
            rec_enabled=False,
        ),
        3: TrackState(
            strip_id=3,
            name="Bass",
            track_type="audio",
            gain_db=0.0,
            pan=0.0,
            muted=True,
            soloed=False,
            rec_enabled=False,
        ),
    }

    state.get_track.side_effect = lambda track_id: tracks.get(track_id)
    state.get_all_tracks.return_value = tracks

    return state


@pytest.fixture
def automation_tools(mock_osc_bridge, mock_state):
    """Create AutomationTools instance with mocked dependencies."""
    return AutomationTools(mock_osc_bridge, mock_state)


class TestAutomationToolsInitialization:
    """Test AutomationTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of AutomationTools."""
        tools = AutomationTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state


class TestSetAutomationMode:
    """Test setting automation mode."""

    @pytest.mark.asyncio
    async def test_set_mode_success_write(self, automation_tools, mock_osc_bridge):
        """Test successfully setting automation mode to write."""
        result = await automation_tools.set_automation_mode(1, "gain", "write")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 2
        )
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["parameter"] == "gain"
        assert result["mode"] == "write"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_set_mode_success_play(self, automation_tools, mock_osc_bridge):
        """Test successfully setting automation mode to play."""
        result = await automation_tools.set_automation_mode(1, "pan", "play")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/pan/automation_mode", 1, 1
        )
        assert result["success"] is True
        assert result["mode"] == "play"

    @pytest.mark.asyncio
    async def test_set_mode_success_off(self, automation_tools, mock_osc_bridge):
        """Test successfully setting automation mode to off."""
        result = await automation_tools.set_automation_mode(1, "gain", "off")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 0
        )
        assert result["success"] is True
        assert result["mode"] == "off"

    @pytest.mark.asyncio
    async def test_set_mode_success_touch(self, automation_tools, mock_osc_bridge):
        """Test successfully setting automation mode to touch."""
        result = await automation_tools.set_automation_mode(1, "gain", "touch")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 3
        )
        assert result["success"] is True
        assert result["mode"] == "touch"

    @pytest.mark.asyncio
    async def test_set_mode_success_latch(self, automation_tools, mock_osc_bridge):
        """Test successfully setting automation mode to latch."""
        result = await automation_tools.set_automation_mode(1, "gain", "latch")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 4
        )
        assert result["success"] is True
        assert result["mode"] == "latch"

    @pytest.mark.asyncio
    async def test_set_mode_case_insensitive(self, automation_tools, mock_osc_bridge):
        """Test mode parameter is case insensitive."""
        result = await automation_tools.set_automation_mode(1, "gain", "WRITE")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 2
        )
        assert result["success"] is True
        assert result["mode"] == "write"

    @pytest.mark.asyncio
    async def test_set_mode_not_connected(self, automation_tools, mock_osc_bridge):
        """Test set mode when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await automation_tools.set_automation_mode(1, "gain", "write")

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_mode_invalid_mode(self, automation_tools, mock_osc_bridge):
        """Test set mode with invalid mode."""
        result = await automation_tools.set_automation_mode(1, "gain", "invalid")

        assert result["success"] is False
        assert "Invalid mode" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_mode_invalid_parameter(self, automation_tools, mock_osc_bridge):
        """Test set mode with invalid parameter."""
        result = await automation_tools.set_automation_mode(1, "invalid_param", "write")

        assert result["success"] is False
        assert "Invalid parameter" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_mode_track_not_found(self, automation_tools):
        """Test set mode with invalid track ID."""
        result = await automation_tools.set_automation_mode(99, "gain", "write")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_set_mode_command_fails(self, automation_tools, mock_osc_bridge):
        """Test handling mode command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await automation_tools.set_automation_mode(1, "gain", "write")

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestGetAutomationMode:
    """Test querying automation mode."""

    @pytest.mark.asyncio
    async def test_get_mode_success(self, automation_tools):
        """Test successfully querying automation mode."""
        result = await automation_tools.get_automation_mode(1, "gain")

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["parameter"] == "gain"
        assert result["mode"] is None  # Not cached
        assert "message" in result

    @pytest.mark.asyncio
    async def test_get_mode_track_not_found(self, automation_tools):
        """Test get mode with invalid track ID."""
        result = await automation_tools.get_automation_mode(99, "gain")

        assert result["success"] is False
        assert "not found" in result["error"]


class TestListAutomationParameters:
    """Test listing automation parameters."""

    @pytest.mark.asyncio
    async def test_list_parameters_success(self, automation_tools):
        """Test successfully listing automation parameters."""
        result = await automation_tools.list_automation_parameters(1)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert "parameters" in result
        assert isinstance(result["parameters"], list)
        assert "gain" in result["parameters"]
        assert "pan" in result["parameters"]
        assert "mute" in result["parameters"]

    @pytest.mark.asyncio
    async def test_list_parameters_track_not_found(self, automation_tools):
        """Test list parameters with invalid track ID."""
        result = await automation_tools.list_automation_parameters(99)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestEnableAutomationWrite:
    """Test enabling automation write mode."""

    @pytest.mark.asyncio
    async def test_enable_write_success(self, automation_tools, mock_osc_bridge):
        """Test successfully enabling automation write."""
        result = await automation_tools.enable_automation_write(1)

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/automation_mode", 1, 2
        )
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_enable_write_not_connected(self, automation_tools, mock_osc_bridge):
        """Test enable write when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await automation_tools.enable_automation_write(1)

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_enable_write_track_not_found(self, automation_tools):
        """Test enable write with invalid track ID."""
        result = await automation_tools.enable_automation_write(99)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_enable_write_command_fails(self, automation_tools, mock_osc_bridge):
        """Test handling enable write command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await automation_tools.enable_automation_write(1)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestDisableAutomationWrite:
    """Test disabling automation write mode."""

    @pytest.mark.asyncio
    async def test_disable_write_success(self, automation_tools, mock_osc_bridge):
        """Test successfully disabling automation write."""
        result = await automation_tools.disable_automation_write(1)

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/automation_mode", 1, 1
        )
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_disable_write_not_connected(
        self, automation_tools, mock_osc_bridge
    ):
        """Test disable write when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await automation_tools.disable_automation_write(1)

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_disable_write_track_not_found(self, automation_tools):
        """Test disable write with invalid track ID."""
        result = await automation_tools.disable_automation_write(99)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestRecordAutomation:
    """Test recording automation for specific parameter."""

    @pytest.mark.asyncio
    async def test_record_automation_success(self, automation_tools, mock_osc_bridge):
        """Test successfully starting automation recording."""
        result = await automation_tools.record_automation(1, "gain")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 2
        )
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["parameter"] == "gain"
        assert result["mode"] == "write"

    @pytest.mark.asyncio
    async def test_record_automation_pan(self, automation_tools, mock_osc_bridge):
        """Test recording automation for pan parameter."""
        result = await automation_tools.record_automation(2, "pan")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/pan/automation_mode", 2, 2
        )
        assert result["success"] is True
        assert result["parameter"] == "pan"


class TestStopAutomationRecording:
    """Test stopping automation recording."""

    @pytest.mark.asyncio
    async def test_stop_recording_success(self, automation_tools, mock_osc_bridge):
        """Test successfully stopping automation recording."""
        result = await automation_tools.stop_automation_recording(1, "gain")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 1
        )
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["parameter"] == "gain"
        assert result["mode"] == "play"

    @pytest.mark.asyncio
    async def test_stop_recording_pan(self, automation_tools, mock_osc_bridge):
        """Test stopping automation recording for pan."""
        result = await automation_tools.stop_automation_recording(2, "pan")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/pan/automation_mode", 2, 1
        )
        assert result["success"] is True
        assert result["parameter"] == "pan"


class TestClearAutomation:
    """Test clearing automation data."""

    @pytest.mark.asyncio
    async def test_clear_automation_all(self, automation_tools, mock_osc_bridge):
        """Test clearing all automation for a parameter."""
        result = await automation_tools.clear_automation(1, "gain")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 0
        )
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["parameter"] == "gain"
        assert result["range"] == "all"

    @pytest.mark.asyncio
    async def test_clear_automation_range(self, automation_tools, mock_osc_bridge):
        """Test clearing automation in a specific range."""
        result = await automation_tools.clear_automation(1, "gain", 1000, 5000)

        # Should still call automation mode (OSC has limited range support)
        mock_osc_bridge.send_command.assert_called_once()
        assert result["success"] is True
        assert "frames 1000-5000" in result["range"]

    @pytest.mark.asyncio
    async def test_clear_automation_track_not_found(self, automation_tools):
        """Test clear automation with invalid track ID."""
        result = await automation_tools.clear_automation(99, "gain")

        assert result["success"] is False
        assert "not found" in result["error"]


class TestHasAutomation:
    """Test checking if automation exists."""

    @pytest.mark.asyncio
    async def test_has_automation_success(self, automation_tools):
        """Test checking automation existence."""
        result = await automation_tools.has_automation(1, "gain")

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["parameter"] == "gain"
        assert result["has_automation"] is None  # Not cached

    @pytest.mark.asyncio
    async def test_has_automation_track_not_found(self, automation_tools):
        """Test has automation with invalid track ID."""
        result = await automation_tools.has_automation(99, "gain")

        assert result["success"] is False
        assert "not found" in result["error"]


class TestCopyAutomation:
    """Test copying automation between tracks."""

    @pytest.mark.asyncio
    async def test_copy_automation_success(self, automation_tools):
        """Test copying automation between tracks."""
        result = await automation_tools.copy_automation(1, 2, "gain")

        assert result["success"] is True
        assert result["source_track"] == 1
        assert result["source_name"] == "Vocals"
        assert result["dest_track"] == 2
        assert result["dest_name"] == "Guitar"
        assert result["parameter"] == "gain"

    @pytest.mark.asyncio
    async def test_copy_automation_source_not_found(self, automation_tools):
        """Test copy automation with invalid source track."""
        result = await automation_tools.copy_automation(99, 2, "gain")

        assert result["success"] is False
        assert "Source track" in result["error"]
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_copy_automation_dest_not_found(self, automation_tools):
        """Test copy automation with invalid destination track."""
        result = await automation_tools.copy_automation(1, 99, "gain")

        assert result["success"] is False
        assert "Destination track" in result["error"]
        assert "not found" in result["error"]


class TestEnableAutomationPlayback:
    """Test enabling automation playback."""

    @pytest.mark.asyncio
    async def test_enable_playback_success(self, automation_tools, mock_osc_bridge):
        """Test successfully enabling automation playback."""
        result = await automation_tools.enable_automation_playback(1, "gain")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 1
        )
        assert result["success"] is True
        assert result["parameter"] == "gain"
        assert result["mode"] == "play"

    @pytest.mark.asyncio
    async def test_enable_playback_pan(self, automation_tools, mock_osc_bridge):
        """Test enabling playback for pan parameter."""
        result = await automation_tools.enable_automation_playback(2, "pan")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/pan/automation_mode", 2, 1
        )
        assert result["success"] is True
        assert result["parameter"] == "pan"


class TestDisableAutomationPlayback:
    """Test disabling automation playback."""

    @pytest.mark.asyncio
    async def test_disable_playback_success(self, automation_tools, mock_osc_bridge):
        """Test successfully disabling automation playback."""
        result = await automation_tools.disable_automation_playback(1, "gain")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/gain/automation_mode", 1, 0
        )
        assert result["success"] is True
        assert result["parameter"] == "gain"
        assert result["mode"] == "off"

    @pytest.mark.asyncio
    async def test_disable_playback_mute(self, automation_tools, mock_osc_bridge):
        """Test disabling playback for mute parameter."""
        result = await automation_tools.disable_automation_playback(3, "mute")

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/mute/automation_mode", 3, 0
        )
        assert result["success"] is True
        assert result["parameter"] == "mute"


class TestGetAutomationState:
    """Test getting complete automation state."""

    @pytest.mark.asyncio
    async def test_get_state_success(self, automation_tools):
        """Test successfully getting automation state."""
        result = await automation_tools.get_automation_state(1, "gain")

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["parameter"] == "gain"
        assert result["mode"] is None
        assert result["has_automation"] is None
        assert result["playback_enabled"] is None

    @pytest.mark.asyncio
    async def test_get_state_track_not_found(self, automation_tools):
        """Test get state with invalid track ID."""
        result = await automation_tools.get_automation_state(99, "gain")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_state_different_parameters(self, automation_tools):
        """Test getting state for different parameters."""
        # Test gain
        result_gain = await automation_tools.get_automation_state(1, "gain")
        assert result_gain["success"] is True
        assert result_gain["parameter"] == "gain"

        # Test pan
        result_pan = await automation_tools.get_automation_state(2, "pan")
        assert result_pan["success"] is True
        assert result_pan["parameter"] == "pan"

        # Test mute
        result_mute = await automation_tools.get_automation_state(3, "mute")
        assert result_mute["success"] is True
        assert result_mute["parameter"] == "mute"
