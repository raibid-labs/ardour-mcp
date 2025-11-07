"""
Tests for advanced mixer control tools.

Tests all advanced mixer-related MCP tools including sends,
plugins, buses, and query operations.
"""

from unittest.mock import Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, TrackState
from ardour_mcp.tools.advanced_mixer import AdvancedMixerTools


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
        1: TrackState(strip_id=1, name="Vocals", track_type="audio",
                     gain_db=-6.0, pan=0.0, muted=False, soloed=False, rec_enabled=False),
        2: TrackState(strip_id=2, name="Guitar", track_type="audio",
                     gain_db=-3.0, pan=-0.5, muted=False, soloed=False, rec_enabled=False),
        3: TrackState(strip_id=3, name="Bass", track_type="audio",
                     gain_db=0.0, pan=0.0, muted=True, soloed=False, rec_enabled=False),
        10: TrackState(strip_id=10, name="Reverb Bus", track_type="audio",
                      gain_db=-12.0, pan=0.0, muted=False, soloed=False, rec_enabled=False),
    }

    state.get_track.side_effect = lambda track_id: tracks.get(track_id)
    state.get_all_tracks.return_value = tracks

    return state


@pytest.fixture
def advanced_mixer_tools(mock_osc_bridge, mock_state):
    """Create AdvancedMixerTools instance with mocked dependencies."""
    return AdvancedMixerTools(mock_osc_bridge, mock_state)


class TestAdvancedMixerToolsInitialization:
    """Test AdvancedMixerTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of AdvancedMixerTools."""
        tools = AdvancedMixerTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state


# ========================================================================
# Send/Return Configuration Tests
# ========================================================================

class TestSetSendLevel:
    """Test set_send_level method."""

    @pytest.mark.asyncio
    async def test_set_send_level_success(self, advanced_mixer_tools, mock_osc_bridge):
        """Test successfully setting send level."""
        result = await advanced_mixer_tools.set_send_level(1, 0, -12.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/send/gain", 1, 0, -12.0)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["send_id"] == 0
        assert result["level_db"] == -12.0
        assert "message" in result

    @pytest.mark.asyncio
    async def test_set_send_level_not_connected(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set send level when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await advanced_mixer_tools.set_send_level(1, 0, -12.0)

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_send_level_track_not_found(self, advanced_mixer_tools):
        """Test set send level with invalid track ID."""
        result = await advanced_mixer_tools.set_send_level(99, 0, -12.0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_set_send_level_out_of_range_low(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set send level with value too low."""
        result = await advanced_mixer_tools.set_send_level(1, 0, -200.0)

        assert result["success"] is False
        assert "out of range" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_send_level_out_of_range_high(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set send level with value too high."""
        result = await advanced_mixer_tools.set_send_level(1, 0, 10.0)

        assert result["success"] is False
        assert "out of range" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_send_level_min_value(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set send level with minimum valid value."""
        result = await advanced_mixer_tools.set_send_level(1, 0, -193.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/send/gain", 1, 0, -193.0)
        assert result["success"] is True
        assert result["level_db"] == -193.0

    @pytest.mark.asyncio
    async def test_set_send_level_max_value(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set send level with maximum valid value."""
        result = await advanced_mixer_tools.set_send_level(1, 0, 6.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/send/gain", 1, 0, 6.0)
        assert result["success"] is True
        assert result["level_db"] == 6.0

    @pytest.mark.asyncio
    async def test_set_send_level_negative_send_id(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set send level with negative send ID."""
        result = await advanced_mixer_tools.set_send_level(1, -1, -12.0)

        assert result["success"] is False
        assert "invalid" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_send_level_command_fails(self, advanced_mixer_tools, mock_osc_bridge):
        """Test handling send level command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await advanced_mixer_tools.set_send_level(1, 0, -12.0)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestEnableSend:
    """Test enable_send method."""

    @pytest.mark.asyncio
    async def test_enable_send_success(self, advanced_mixer_tools, mock_osc_bridge):
        """Test successfully enabling a send."""
        result = await advanced_mixer_tools.enable_send(1, 0, True)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/send/enable", 1, 0, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["send_id"] == 0
        assert result["enabled"] is True
        assert "Enabled" in result["message"]

    @pytest.mark.asyncio
    async def test_disable_send_success(self, advanced_mixer_tools, mock_osc_bridge):
        """Test successfully disabling a send."""
        result = await advanced_mixer_tools.enable_send(1, 0, False)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/send/enable", 1, 0, 0)
        assert result["success"] is True
        assert result["enabled"] is False
        assert "Disabled" in result["message"]

    @pytest.mark.asyncio
    async def test_enable_send_not_connected(self, advanced_mixer_tools, mock_osc_bridge):
        """Test enable send when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await advanced_mixer_tools.enable_send(1, 0, True)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_enable_send_track_not_found(self, advanced_mixer_tools):
        """Test enable send with invalid track ID."""
        result = await advanced_mixer_tools.enable_send(99, 0, True)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_enable_send_negative_send_id(self, advanced_mixer_tools, mock_osc_bridge):
        """Test enable send with negative send ID."""
        result = await advanced_mixer_tools.enable_send(1, -1, True)

        assert result["success"] is False
        assert "invalid" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_enable_send_command_fails(self, advanced_mixer_tools, mock_osc_bridge):
        """Test handling enable send command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await advanced_mixer_tools.enable_send(1, 0, True)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestToggleSend:
    """Test toggle_send method."""

    @pytest.mark.asyncio
    async def test_toggle_send_success(self, advanced_mixer_tools, mock_osc_bridge):
        """Test successfully toggling a send."""
        result = await advanced_mixer_tools.toggle_send(1, 0)

        # Should default to enabling
        mock_osc_bridge.send_command.assert_called_once_with("/strip/send/enable", 1, 0, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["send_id"] == 0
        assert result["enabled"] is True

    @pytest.mark.asyncio
    async def test_toggle_send_not_connected(self, advanced_mixer_tools, mock_osc_bridge):
        """Test toggle send when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await advanced_mixer_tools.toggle_send(1, 0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_toggle_send_track_not_found(self, advanced_mixer_tools):
        """Test toggle send with invalid track ID."""
        result = await advanced_mixer_tools.toggle_send(99, 0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_toggle_send_negative_send_id(self, advanced_mixer_tools, mock_osc_bridge):
        """Test toggle send with negative send ID."""
        result = await advanced_mixer_tools.toggle_send(1, -1)

        assert result["success"] is False
        assert "invalid" in result["error"]


class TestListSends:
    """Test list_sends method."""

    @pytest.mark.asyncio
    async def test_list_sends_success(self, advanced_mixer_tools):
        """Test successfully listing sends."""
        result = await advanced_mixer_tools.list_sends(1)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["send_count"] == 0  # Not cached
        assert "sends" in result

    @pytest.mark.asyncio
    async def test_list_sends_track_not_found(self, advanced_mixer_tools):
        """Test list sends with invalid track ID."""
        result = await advanced_mixer_tools.list_sends(99)

        assert result["success"] is False
        assert "not found" in result["error"]


# ========================================================================
# Plugin Control Tests
# ========================================================================

class TestSetPluginParameter:
    """Test set_plugin_parameter method."""

    @pytest.mark.asyncio
    async def test_set_plugin_parameter_success(self, advanced_mixer_tools, mock_osc_bridge):
        """Test successfully setting plugin parameter."""
        result = await advanced_mixer_tools.set_plugin_parameter(1, 0, 2, 0.5)

        mock_osc_bridge.send_command.assert_called_once_with(
            "/strip/plugin/parameter", 1, 0, 2, 0.5
        )
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["plugin_id"] == 0
        assert result["param_id"] == 2
        assert result["value"] == 0.5

    @pytest.mark.asyncio
    async def test_set_plugin_parameter_not_connected(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set plugin parameter when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await advanced_mixer_tools.set_plugin_parameter(1, 0, 2, 0.5)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_plugin_parameter_track_not_found(self, advanced_mixer_tools):
        """Test set plugin parameter with invalid track ID."""
        result = await advanced_mixer_tools.set_plugin_parameter(99, 0, 2, 0.5)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_set_plugin_parameter_negative_plugin_id(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set plugin parameter with negative plugin ID."""
        result = await advanced_mixer_tools.set_plugin_parameter(1, -1, 2, 0.5)

        assert result["success"] is False
        assert "invalid" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_plugin_parameter_negative_param_id(self, advanced_mixer_tools, mock_osc_bridge):
        """Test set plugin parameter with negative param ID."""
        result = await advanced_mixer_tools.set_plugin_parameter(1, 0, -1, 0.5)

        assert result["success"] is False
        assert "invalid" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_plugin_parameter_command_fails(self, advanced_mixer_tools, mock_osc_bridge):
        """Test handling plugin parameter command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await advanced_mixer_tools.set_plugin_parameter(1, 0, 2, 0.5)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestActivatePlugin:
    """Test activate_plugin method."""

    @pytest.mark.asyncio
    async def test_activate_plugin_success(self, advanced_mixer_tools, mock_osc_bridge):
        """Test successfully activating a plugin."""
        result = await advanced_mixer_tools.activate_plugin(1, 0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/plugin/activate", 1, 0, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["plugin_id"] == 0
        assert result["active"] is True
        assert "Activated" in result["message"]

    @pytest.mark.asyncio
    async def test_activate_plugin_not_connected(self, advanced_mixer_tools, mock_osc_bridge):
        """Test activate plugin when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await advanced_mixer_tools.activate_plugin(1, 0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_activate_plugin_track_not_found(self, advanced_mixer_tools):
        """Test activate plugin with invalid track ID."""
        result = await advanced_mixer_tools.activate_plugin(99, 0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_activate_plugin_negative_plugin_id(self, advanced_mixer_tools, mock_osc_bridge):
        """Test activate plugin with negative plugin ID."""
        result = await advanced_mixer_tools.activate_plugin(1, -1)

        assert result["success"] is False
        assert "invalid" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_activate_plugin_command_fails(self, advanced_mixer_tools, mock_osc_bridge):
        """Test handling activate plugin command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await advanced_mixer_tools.activate_plugin(1, 0)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestDeactivatePlugin:
    """Test deactivate_plugin method."""

    @pytest.mark.asyncio
    async def test_deactivate_plugin_success(self, advanced_mixer_tools, mock_osc_bridge):
        """Test successfully deactivating a plugin."""
        result = await advanced_mixer_tools.deactivate_plugin(1, 0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/plugin/activate", 1, 0, 0)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["plugin_id"] == 0
        assert result["active"] is False
        assert "Deactivated" in result["message"]

    @pytest.mark.asyncio
    async def test_deactivate_plugin_not_connected(self, advanced_mixer_tools, mock_osc_bridge):
        """Test deactivate plugin when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await advanced_mixer_tools.deactivate_plugin(1, 0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_deactivate_plugin_track_not_found(self, advanced_mixer_tools):
        """Test deactivate plugin with invalid track ID."""
        result = await advanced_mixer_tools.deactivate_plugin(99, 0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_deactivate_plugin_negative_plugin_id(self, advanced_mixer_tools, mock_osc_bridge):
        """Test deactivate plugin with negative plugin ID."""
        result = await advanced_mixer_tools.deactivate_plugin(1, -1)

        assert result["success"] is False
        assert "invalid" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_deactivate_plugin_command_fails(self, advanced_mixer_tools, mock_osc_bridge):
        """Test handling deactivate plugin command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await advanced_mixer_tools.deactivate_plugin(1, 0)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestTogglePlugin:
    """Test toggle_plugin method."""

    @pytest.mark.asyncio
    async def test_toggle_plugin_success(self, advanced_mixer_tools, mock_osc_bridge):
        """Test successfully toggling a plugin."""
        result = await advanced_mixer_tools.toggle_plugin(1, 0)

        # Should default to activating
        mock_osc_bridge.send_command.assert_called_once_with("/strip/plugin/activate", 1, 0, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["plugin_id"] == 0
        assert result["active"] is True

    @pytest.mark.asyncio
    async def test_toggle_plugin_not_connected(self, advanced_mixer_tools, mock_osc_bridge):
        """Test toggle plugin when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await advanced_mixer_tools.toggle_plugin(1, 0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_toggle_plugin_track_not_found(self, advanced_mixer_tools):
        """Test toggle plugin with invalid track ID."""
        result = await advanced_mixer_tools.toggle_plugin(99, 0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_toggle_plugin_negative_plugin_id(self, advanced_mixer_tools, mock_osc_bridge):
        """Test toggle plugin with negative plugin ID."""
        result = await advanced_mixer_tools.toggle_plugin(1, -1)

        assert result["success"] is False
        assert "invalid" in result["error"]


class TestGetPluginInfo:
    """Test get_plugin_info method."""

    @pytest.mark.asyncio
    async def test_get_plugin_info_success(self, advanced_mixer_tools):
        """Test successfully getting plugin info."""
        result = await advanced_mixer_tools.get_plugin_info(1, 0)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["plugin_id"] == 0
        assert "name" in result
        assert "param_count" in result

    @pytest.mark.asyncio
    async def test_get_plugin_info_track_not_found(self, advanced_mixer_tools):
        """Test get plugin info with invalid track ID."""
        result = await advanced_mixer_tools.get_plugin_info(99, 0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_plugin_info_negative_plugin_id(self, advanced_mixer_tools):
        """Test get plugin info with negative plugin ID."""
        result = await advanced_mixer_tools.get_plugin_info(1, -1)

        assert result["success"] is False
        assert "invalid" in result["error"]


# ========================================================================
# Bus Operations Tests
# ========================================================================

class TestListBuses:
    """Test list_buses method."""

    @pytest.mark.asyncio
    async def test_list_buses_success(self, advanced_mixer_tools):
        """Test successfully listing buses."""
        result = await advanced_mixer_tools.list_buses()

        assert result["success"] is True
        assert "bus_count" in result
        assert "buses" in result
        assert isinstance(result["buses"], list)


class TestGetBusInfo:
    """Test get_bus_info method."""

    @pytest.mark.asyncio
    async def test_get_bus_info_success(self, advanced_mixer_tools):
        """Test successfully getting bus info."""
        result = await advanced_mixer_tools.get_bus_info(10)

        assert result["success"] is True
        assert result["bus_id"] == 10
        assert result["name"] == "Reverb Bus"
        assert "gain_db" in result

    @pytest.mark.asyncio
    async def test_get_bus_info_not_found(self, advanced_mixer_tools):
        """Test get bus info with invalid bus ID."""
        result = await advanced_mixer_tools.get_bus_info(99)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestListBusSends:
    """Test list_bus_sends method."""

    @pytest.mark.asyncio
    async def test_list_bus_sends_success(self, advanced_mixer_tools):
        """Test successfully listing bus sends."""
        result = await advanced_mixer_tools.list_bus_sends(10)

        assert result["success"] is True
        assert result["bus_id"] == 10
        assert result["bus_name"] == "Reverb Bus"
        assert "send_count" in result
        assert "sends" in result

    @pytest.mark.asyncio
    async def test_list_bus_sends_not_found(self, advanced_mixer_tools):
        """Test list bus sends with invalid bus ID."""
        result = await advanced_mixer_tools.list_bus_sends(99)

        assert result["success"] is False
        assert "not found" in result["error"]


# ========================================================================
# Query Methods Tests
# ========================================================================

class TestGetSendLevel:
    """Test get_send_level method."""

    @pytest.mark.asyncio
    async def test_get_send_level_success(self, advanced_mixer_tools):
        """Test successfully getting send level."""
        result = await advanced_mixer_tools.get_send_level(1, 0)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["send_id"] == 0
        assert "level_db" in result

    @pytest.mark.asyncio
    async def test_get_send_level_track_not_found(self, advanced_mixer_tools):
        """Test get send level with invalid track ID."""
        result = await advanced_mixer_tools.get_send_level(99, 0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_send_level_negative_send_id(self, advanced_mixer_tools):
        """Test get send level with negative send ID."""
        result = await advanced_mixer_tools.get_send_level(1, -1)

        assert result["success"] is False
        assert "invalid" in result["error"]


class TestGetPluginParameters:
    """Test get_plugin_parameters method."""

    @pytest.mark.asyncio
    async def test_get_plugin_parameters_success(self, advanced_mixer_tools):
        """Test successfully getting plugin parameters."""
        result = await advanced_mixer_tools.get_plugin_parameters(1, 0)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["plugin_id"] == 0
        assert "param_count" in result
        assert "parameters" in result

    @pytest.mark.asyncio
    async def test_get_plugin_parameters_track_not_found(self, advanced_mixer_tools):
        """Test get plugin parameters with invalid track ID."""
        result = await advanced_mixer_tools.get_plugin_parameters(99, 0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_plugin_parameters_negative_plugin_id(self, advanced_mixer_tools):
        """Test get plugin parameters with negative plugin ID."""
        result = await advanced_mixer_tools.get_plugin_parameters(1, -1)

        assert result["success"] is False
        assert "invalid" in result["error"]


class TestGetTrackSendsCount:
    """Test get_track_sends_count method."""

    @pytest.mark.asyncio
    async def test_get_track_sends_count_success(self, advanced_mixer_tools):
        """Test successfully getting track sends count."""
        result = await advanced_mixer_tools.get_track_sends_count(1)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert "send_count" in result

    @pytest.mark.asyncio
    async def test_get_track_sends_count_track_not_found(self, advanced_mixer_tools):
        """Test get track sends count with invalid track ID."""
        result = await advanced_mixer_tools.get_track_sends_count(99)

        assert result["success"] is False
        assert "not found" in result["error"]
