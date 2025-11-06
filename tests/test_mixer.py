"""
Tests for mixer control tools.

Tests all mixer-related MCP tools including volume, pan,
mute, solo, rec enable, and batch operations.
"""

from unittest.mock import Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, TrackState
from ardour_mcp.tools.mixer import MixerTools


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
        4: TrackState(strip_id=4, name="Drums", track_type="audio",
                     gain_db=2.0, pan=0.0, muted=False, soloed=True, rec_enabled=False),
        5: TrackState(strip_id=5, name="Keys", track_type="midi",
                     gain_db=-12.0, pan=0.5, muted=False, soloed=False, rec_enabled=True),
    }

    state.get_track.side_effect = lambda track_id: tracks.get(track_id)
    state.get_all_tracks.return_value = tracks

    return state


@pytest.fixture
def mixer_tools(mock_osc_bridge, mock_state):
    """Create MixerTools instance with mocked dependencies."""
    return MixerTools(mock_osc_bridge, mock_state)


class TestMixerToolsInitialization:
    """Test MixerTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of MixerTools."""
        tools = MixerTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state


class TestSetTrackVolume:
    """Test track volume control."""

    @pytest.mark.asyncio
    async def test_set_volume_success(self, mixer_tools, mock_osc_bridge):
        """Test successfully setting track volume."""
        result = await mixer_tools.set_track_volume(1, -6.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/gain", 1, -6.0)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["volume_db"] == -6.0
        assert "message" in result

    @pytest.mark.asyncio
    async def test_set_volume_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test set volume when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.set_track_volume(1, -6.0)

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_volume_track_not_found(self, mixer_tools, mock_state):
        """Test set volume with invalid track ID."""
        result = await mixer_tools.set_track_volume(99, -6.0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_set_volume_out_of_range_low(self, mixer_tools, mock_osc_bridge):
        """Test set volume with value too low."""
        result = await mixer_tools.set_track_volume(1, -200.0)

        assert result["success"] is False
        assert "out of range" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_volume_out_of_range_high(self, mixer_tools, mock_osc_bridge):
        """Test set volume with value too high."""
        result = await mixer_tools.set_track_volume(1, 10.0)

        assert result["success"] is False
        assert "out of range" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_volume_min_value(self, mixer_tools, mock_osc_bridge):
        """Test set volume with minimum valid value."""
        result = await mixer_tools.set_track_volume(1, -193.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/gain", 1, -193.0)
        assert result["success"] is True
        assert result["volume_db"] == -193.0

    @pytest.mark.asyncio
    async def test_set_volume_max_value(self, mixer_tools, mock_osc_bridge):
        """Test set volume with maximum valid value."""
        result = await mixer_tools.set_track_volume(1, 6.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/gain", 1, 6.0)
        assert result["success"] is True
        assert result["volume_db"] == 6.0

    @pytest.mark.asyncio
    async def test_set_volume_command_fails(self, mixer_tools, mock_osc_bridge):
        """Test handling volume command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await mixer_tools.set_track_volume(1, -6.0)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestSetTrackPan:
    """Test track pan control."""

    @pytest.mark.asyncio
    async def test_set_pan_success_center(self, mixer_tools, mock_osc_bridge):
        """Test successfully setting pan to center."""
        result = await mixer_tools.set_track_pan(1, 0.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/pan_stereo_position", 1, 0.0)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["pan"] == 0.0
        assert "center" in result["message"]

    @pytest.mark.asyncio
    async def test_set_pan_success_left(self, mixer_tools, mock_osc_bridge):
        """Test successfully setting pan left."""
        result = await mixer_tools.set_track_pan(1, -0.5)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/pan_stereo_position", 1, -0.5)
        assert result["success"] is True
        assert result["pan"] == -0.5
        assert "left" in result["message"]

    @pytest.mark.asyncio
    async def test_set_pan_success_right(self, mixer_tools, mock_osc_bridge):
        """Test successfully setting pan right."""
        result = await mixer_tools.set_track_pan(1, 0.7)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/pan_stereo_position", 1, 0.7)
        assert result["success"] is True
        assert result["pan"] == 0.7
        assert "right" in result["message"]

    @pytest.mark.asyncio
    async def test_set_pan_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test set pan when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.set_track_pan(1, 0.0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_pan_track_not_found(self, mixer_tools):
        """Test set pan with invalid track ID."""
        result = await mixer_tools.set_track_pan(99, 0.0)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_set_pan_out_of_range_low(self, mixer_tools, mock_osc_bridge):
        """Test set pan with value too low."""
        result = await mixer_tools.set_track_pan(1, -1.5)

        assert result["success"] is False
        assert "out of range" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_pan_out_of_range_high(self, mixer_tools, mock_osc_bridge):
        """Test set pan with value too high."""
        result = await mixer_tools.set_track_pan(1, 1.5)

        assert result["success"] is False
        assert "out of range" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_pan_hard_left(self, mixer_tools, mock_osc_bridge):
        """Test set pan to hard left."""
        result = await mixer_tools.set_track_pan(1, -1.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/pan_stereo_position", 1, -1.0)
        assert result["success"] is True
        assert result["pan"] == -1.0

    @pytest.mark.asyncio
    async def test_set_pan_hard_right(self, mixer_tools, mock_osc_bridge):
        """Test set pan to hard right."""
        result = await mixer_tools.set_track_pan(1, 1.0)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/pan_stereo_position", 1, 1.0)
        assert result["success"] is True
        assert result["pan"] == 1.0


class TestSetTrackMute:
    """Test track mute control."""

    @pytest.mark.asyncio
    async def test_set_mute_true(self, mixer_tools, mock_osc_bridge):
        """Test muting a track."""
        result = await mixer_tools.set_track_mute(1, True)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/mute", 1, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["muted"] is True
        assert "Muted" in result["message"]

    @pytest.mark.asyncio
    async def test_set_mute_false(self, mixer_tools, mock_osc_bridge):
        """Test unmuting a track."""
        result = await mixer_tools.set_track_mute(1, False)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/mute", 1, 0)
        assert result["success"] is True
        assert result["muted"] is False
        assert "Unmuted" in result["message"]

    @pytest.mark.asyncio
    async def test_set_mute_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test set mute when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.set_track_mute(1, True)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_mute_track_not_found(self, mixer_tools):
        """Test set mute with invalid track ID."""
        result = await mixer_tools.set_track_mute(99, True)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestToggleTrackMute:
    """Test track mute toggle."""

    @pytest.mark.asyncio
    async def test_toggle_mute_from_unmuted(self, mixer_tools, mock_osc_bridge):
        """Test toggling mute from unmuted state."""
        result = await mixer_tools.toggle_track_mute(1)  # Track 1 is unmuted

        mock_osc_bridge.send_command.assert_called_once_with("/strip/mute", 1, 1)
        assert result["success"] is True
        assert result["muted"] is True

    @pytest.mark.asyncio
    async def test_toggle_mute_from_muted(self, mixer_tools, mock_osc_bridge):
        """Test toggling mute from muted state."""
        result = await mixer_tools.toggle_track_mute(3)  # Track 3 is muted

        mock_osc_bridge.send_command.assert_called_once_with("/strip/mute", 3, 0)
        assert result["success"] is True
        assert result["muted"] is False

    @pytest.mark.asyncio
    async def test_toggle_mute_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test toggle mute when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.toggle_track_mute(1)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_toggle_mute_track_not_found(self, mixer_tools):
        """Test toggle mute with invalid track ID."""
        result = await mixer_tools.toggle_track_mute(99)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestSetTrackSolo:
    """Test track solo control."""

    @pytest.mark.asyncio
    async def test_set_solo_true(self, mixer_tools, mock_osc_bridge):
        """Test soloing a track."""
        result = await mixer_tools.set_track_solo(1, True)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/solo", 1, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["soloed"] is True
        assert "Soloed" in result["message"]

    @pytest.mark.asyncio
    async def test_set_solo_false(self, mixer_tools, mock_osc_bridge):
        """Test unsoloing a track."""
        result = await mixer_tools.set_track_solo(1, False)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/solo", 1, 0)
        assert result["success"] is True
        assert result["soloed"] is False
        assert "Unsoloed" in result["message"]

    @pytest.mark.asyncio
    async def test_set_solo_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test set solo when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.set_track_solo(1, True)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_solo_track_not_found(self, mixer_tools):
        """Test set solo with invalid track ID."""
        result = await mixer_tools.set_track_solo(99, True)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestToggleTrackSolo:
    """Test track solo toggle."""

    @pytest.mark.asyncio
    async def test_toggle_solo_from_unsoloed(self, mixer_tools, mock_osc_bridge):
        """Test toggling solo from unsoloed state."""
        result = await mixer_tools.toggle_track_solo(1)  # Track 1 is unsoloed

        mock_osc_bridge.send_command.assert_called_once_with("/strip/solo", 1, 1)
        assert result["success"] is True
        assert result["soloed"] is True

    @pytest.mark.asyncio
    async def test_toggle_solo_from_soloed(self, mixer_tools, mock_osc_bridge):
        """Test toggling solo from soloed state."""
        result = await mixer_tools.toggle_track_solo(4)  # Track 4 is soloed

        mock_osc_bridge.send_command.assert_called_once_with("/strip/solo", 4, 0)
        assert result["success"] is True
        assert result["soloed"] is False

    @pytest.mark.asyncio
    async def test_toggle_solo_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test toggle solo when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.toggle_track_solo(1)

        assert result["success"] is False
        assert "Not connected" in result["error"]


class TestSetTrackRecEnable:
    """Test track record enable control."""

    @pytest.mark.asyncio
    async def test_set_rec_enable_true(self, mixer_tools, mock_osc_bridge):
        """Test arming a track for recording."""
        result = await mixer_tools.set_track_rec_enable(1, True)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/recenable", 1, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["rec_enabled"] is True
        assert "Armed" in result["message"]

    @pytest.mark.asyncio
    async def test_set_rec_enable_false(self, mixer_tools, mock_osc_bridge):
        """Test disarming a track from recording."""
        result = await mixer_tools.set_track_rec_enable(1, False)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/recenable", 1, 0)
        assert result["success"] is True
        assert result["rec_enabled"] is False
        assert "Disarmed" in result["message"]

    @pytest.mark.asyncio
    async def test_set_rec_enable_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test set rec enable when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.set_track_rec_enable(1, True)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_rec_enable_track_not_found(self, mixer_tools):
        """Test set rec enable with invalid track ID."""
        result = await mixer_tools.set_track_rec_enable(99, True)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestToggleTrackRecEnable:
    """Test track record enable toggle."""

    @pytest.mark.asyncio
    async def test_toggle_rec_enable_from_disabled(self, mixer_tools, mock_osc_bridge):
        """Test toggling rec enable from disabled state."""
        result = await mixer_tools.toggle_track_rec_enable(1)  # Track 1 is not armed

        mock_osc_bridge.send_command.assert_called_once_with("/strip/recenable", 1, 1)
        assert result["success"] is True
        assert result["rec_enabled"] is True

    @pytest.mark.asyncio
    async def test_toggle_rec_enable_from_enabled(self, mixer_tools, mock_osc_bridge):
        """Test toggling rec enable from enabled state."""
        result = await mixer_tools.toggle_track_rec_enable(5)  # Track 5 is armed

        mock_osc_bridge.send_command.assert_called_once_with("/strip/recenable", 5, 0)
        assert result["success"] is True
        assert result["rec_enabled"] is False

    @pytest.mark.asyncio
    async def test_toggle_rec_enable_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test toggle rec enable when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.toggle_track_rec_enable(1)

        assert result["success"] is False
        assert "Not connected" in result["error"]


class TestArmTrackForRecording:
    """Test arm track convenience method."""

    @pytest.mark.asyncio
    async def test_arm_track_success(self, mixer_tools, mock_osc_bridge):
        """Test arming a track using convenience method."""
        result = await mixer_tools.arm_track_for_recording(1)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/recenable", 1, 1)
        assert result["success"] is True
        assert result["rec_enabled"] is True

    @pytest.mark.asyncio
    async def test_arm_track_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test arm track when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.arm_track_for_recording(1)

        assert result["success"] is False
        assert "Not connected" in result["error"]


class TestDisarmTrack:
    """Test disarm track convenience method."""

    @pytest.mark.asyncio
    async def test_disarm_track_success(self, mixer_tools, mock_osc_bridge):
        """Test disarming a track using convenience method."""
        result = await mixer_tools.disarm_track(1)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/recenable", 1, 0)
        assert result["success"] is True
        assert result["rec_enabled"] is False

    @pytest.mark.asyncio
    async def test_disarm_track_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test disarm track when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.disarm_track(1)

        assert result["success"] is False
        assert "Not connected" in result["error"]


class TestMuteAllTracks:
    """Test mute all tracks batch operation."""

    @pytest.mark.asyncio
    async def test_mute_all_success(self, mixer_tools, mock_osc_bridge):
        """Test successfully muting all tracks."""
        result = await mixer_tools.mute_all_tracks()

        assert result["success"] is True
        assert result["tracks_muted"] == 5
        assert result["total_tracks"] == 5
        assert "failed_tracks" not in result
        # Verify all tracks were sent mute commands
        assert mock_osc_bridge.send_command.call_count == 5

    @pytest.mark.asyncio
    async def test_mute_all_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test mute all when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.mute_all_tracks()

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_mute_all_no_tracks(self, mixer_tools, mock_state):
        """Test mute all when no tracks exist."""
        mock_state.get_all_tracks.return_value = {}

        result = await mixer_tools.mute_all_tracks()

        assert result["success"] is True
        assert result["tracks_muted"] == 0
        assert result["total_tracks"] == 0

    @pytest.mark.asyncio
    async def test_mute_all_partial_failure(self, mixer_tools, mock_osc_bridge, mock_state):
        """Test mute all with some tracks failing."""
        # Make track 3 fail
        call_count = [0]

        def send_command_side_effect(*args, **kwargs):
            call_count[0] += 1
            # Fail on the 3rd call (track 3)
            return call_count[0] != 3

        mock_osc_bridge.send_command.side_effect = send_command_side_effect

        result = await mixer_tools.mute_all_tracks()

        assert result["success"] is False
        assert result["tracks_muted"] == 4
        assert result["total_tracks"] == 5
        assert "failed_tracks" in result
        assert 3 in result["failed_tracks"]


class TestUnmuteAllTracks:
    """Test unmute all tracks batch operation."""

    @pytest.mark.asyncio
    async def test_unmute_all_success(self, mixer_tools, mock_osc_bridge):
        """Test successfully unmuting all tracks."""
        result = await mixer_tools.unmute_all_tracks()

        assert result["success"] is True
        assert result["tracks_unmuted"] == 5
        assert result["total_tracks"] == 5
        assert "failed_tracks" not in result
        # Verify all tracks were sent unmute commands
        assert mock_osc_bridge.send_command.call_count == 5

    @pytest.mark.asyncio
    async def test_unmute_all_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test unmute all when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.unmute_all_tracks()

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_unmute_all_no_tracks(self, mixer_tools, mock_state):
        """Test unmute all when no tracks exist."""
        mock_state.get_all_tracks.return_value = {}

        result = await mixer_tools.unmute_all_tracks()

        assert result["success"] is True
        assert result["tracks_unmuted"] == 0
        assert result["total_tracks"] == 0


class TestClearAllSolos:
    """Test clear all solos batch operation."""

    @pytest.mark.asyncio
    async def test_clear_all_solos_success(self, mixer_tools, mock_osc_bridge):
        """Test successfully clearing all solos."""
        result = await mixer_tools.clear_all_solos()

        assert result["success"] is True
        assert result["tracks_unsoloed"] == 5
        assert result["total_tracks"] == 5
        assert "failed_tracks" not in result
        # Verify all tracks were sent unsolo commands
        assert mock_osc_bridge.send_command.call_count == 5

    @pytest.mark.asyncio
    async def test_clear_all_solos_not_connected(self, mixer_tools, mock_osc_bridge):
        """Test clear all solos when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await mixer_tools.clear_all_solos()

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_clear_all_solos_no_tracks(self, mixer_tools, mock_state):
        """Test clear all solos when no tracks exist."""
        mock_state.get_all_tracks.return_value = {}

        result = await mixer_tools.clear_all_solos()

        assert result["success"] is True
        assert result["tracks_unsoloed"] == 0
        assert result["total_tracks"] == 0


class TestGetTrackMixerState:
    """Test getting track mixer state."""

    @pytest.mark.asyncio
    async def test_get_mixer_state_success(self, mixer_tools):
        """Test getting mixer state for a track."""
        result = await mixer_tools.get_track_mixer_state(1)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["track_type"] == "audio"
        assert result["gain_db"] == -6.0
        assert result["pan"] == 0.0
        assert result["muted"] is False
        assert result["soloed"] is False
        assert result["rec_enabled"] is False

    @pytest.mark.asyncio
    async def test_get_mixer_state_midi_track(self, mixer_tools):
        """Test getting mixer state for a MIDI track."""
        result = await mixer_tools.get_track_mixer_state(5)

        assert result["success"] is True
        assert result["track_id"] == 5
        assert result["track_name"] == "Keys"
        assert result["track_type"] == "midi"
        assert result["gain_db"] == -12.0
        assert result["pan"] == 0.5
        assert result["rec_enabled"] is True

    @pytest.mark.asyncio
    async def test_get_mixer_state_muted_track(self, mixer_tools):
        """Test getting mixer state for a muted track."""
        result = await mixer_tools.get_track_mixer_state(3)

        assert result["success"] is True
        assert result["track_name"] == "Bass"
        assert result["muted"] is True

    @pytest.mark.asyncio
    async def test_get_mixer_state_soloed_track(self, mixer_tools):
        """Test getting mixer state for a soloed track."""
        result = await mixer_tools.get_track_mixer_state(4)

        assert result["success"] is True
        assert result["track_name"] == "Drums"
        assert result["soloed"] is True

    @pytest.mark.asyncio
    async def test_get_mixer_state_track_not_found(self, mixer_tools):
        """Test getting mixer state for non-existent track."""
        result = await mixer_tools.get_track_mixer_state(99)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestMixerToolsIntegration:
    """Integration tests for mixer tools."""

    @pytest.mark.asyncio
    async def test_volume_and_pan_workflow(self, mixer_tools, mock_osc_bridge):
        """Test setting volume and pan in sequence."""
        # Set volume
        volume_result = await mixer_tools.set_track_volume(1, -3.0)
        assert volume_result["success"] is True

        # Set pan
        mock_osc_bridge.reset_mock()
        pan_result = await mixer_tools.set_track_pan(1, -0.5)
        assert pan_result["success"] is True

    @pytest.mark.asyncio
    async def test_mute_solo_workflow(self, mixer_tools, mock_osc_bridge):
        """Test mute and solo operations."""
        # Mute track
        mute_result = await mixer_tools.set_track_mute(1, True)
        assert mute_result["success"] is True

        # Solo another track
        mock_osc_bridge.reset_mock()
        solo_result = await mixer_tools.set_track_solo(2, True)
        assert solo_result["success"] is True

        # Clear all solos
        mock_osc_bridge.reset_mock()
        clear_result = await mixer_tools.clear_all_solos()
        assert clear_result["success"] is True

    @pytest.mark.asyncio
    async def test_recording_workflow(self, mixer_tools, mock_osc_bridge):
        """Test record arming workflow."""
        # Arm track
        arm_result = await mixer_tools.arm_track_for_recording(1)
        assert arm_result["success"] is True
        assert arm_result["rec_enabled"] is True

        # Disarm track
        mock_osc_bridge.reset_mock()
        disarm_result = await mixer_tools.disarm_track(1)
        assert disarm_result["success"] is True
        assert disarm_result["rec_enabled"] is False

    @pytest.mark.asyncio
    async def test_batch_operations_workflow(self, mixer_tools, mock_osc_bridge):
        """Test batch operations in sequence."""
        # Mute all
        mute_result = await mixer_tools.mute_all_tracks()
        assert mute_result["success"] is True
        assert mute_result["tracks_muted"] == 5

        # Unmute all
        mock_osc_bridge.reset_mock()
        unmute_result = await mixer_tools.unmute_all_tracks()
        assert unmute_result["success"] is True
        assert unmute_result["tracks_unmuted"] == 5

    @pytest.mark.asyncio
    async def test_mixer_state_query_workflow(self, mixer_tools, mock_osc_bridge):
        """Test querying mixer state after changes."""
        # Set volume
        await mixer_tools.set_track_volume(1, -12.0)

        # Query state (uses cached state)
        state_result = await mixer_tools.get_track_mixer_state(1)
        assert state_result["success"] is True
        assert state_result["track_id"] == 1

    @pytest.mark.asyncio
    async def test_toggle_operations(self, mixer_tools, mock_osc_bridge):
        """Test all toggle operations."""
        # Toggle mute
        mute_result = await mixer_tools.toggle_track_mute(1)
        assert mute_result["success"] is True

        # Toggle solo
        mock_osc_bridge.reset_mock()
        solo_result = await mixer_tools.toggle_track_solo(1)
        assert solo_result["success"] is True

        # Toggle rec enable
        mock_osc_bridge.reset_mock()
        rec_result = await mixer_tools.toggle_track_rec_enable(1)
        assert rec_result["success"] is True
