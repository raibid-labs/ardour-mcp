"""
Tests for recording control tools.

Tests all recording-related MCP tools including global recording control,
punch recording, input monitoring, and recording state queries.
"""

from unittest.mock import Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, TrackState, TransportState
from ardour_mcp.tools.recording import RecordingTools


@pytest.fixture
def mock_osc_bridge():
    """Create a mock OSC bridge for testing."""
    bridge = Mock()
    bridge.is_connected.return_value = True
    bridge.send_command.return_value = True
    return bridge


@pytest.fixture
def mock_state():
    """Create a mock state with sample tracks and transport state."""
    state = Mock(spec=ArdourState)

    # Create sample tracks with some armed for recording
    tracks = {
        1: TrackState(strip_id=1, name="Vocals", track_type="audio",
                     rec_enabled=True, muted=False),
        2: TrackState(strip_id=2, name="Guitar", track_type="audio",
                     rec_enabled=False, muted=False),
        3: TrackState(strip_id=3, name="Bass", track_type="audio",
                     rec_enabled=True, muted=False),
        4: TrackState(strip_id=4, name="Drums", track_type="audio",
                     rec_enabled=False, muted=False),
        5: TrackState(strip_id=5, name="Keys", track_type="midi",
                     rec_enabled=False, muted=False),
    }

    # Create transport state
    transport = TransportState(
        playing=False,
        recording=False,
        frame=0,
        tempo=120.0,
        time_signature=(4, 4)
    )

    state.get_track.side_effect = lambda track_id: tracks.get(track_id)
    state.get_all_tracks.return_value = tracks
    state.get_transport.return_value = transport

    return state


@pytest.fixture
def recording_tools(mock_osc_bridge, mock_state):
    """Create RecordingTools instance with mocked dependencies."""
    return RecordingTools(mock_osc_bridge, mock_state)


class TestRecordingToolsInitialization:
    """Test RecordingTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of RecordingTools."""
        tools = RecordingTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state


class TestStartRecording:
    """Test start_recording method."""

    @pytest.mark.asyncio
    async def test_start_recording_success(self, recording_tools, mock_osc_bridge):
        """Test successfully starting recording."""
        result = await recording_tools.start_recording()

        # Should send rec_enable_toggle and transport_play
        assert mock_osc_bridge.send_command.call_count == 2
        mock_osc_bridge.send_command.assert_any_call("/rec_enable_toggle")
        mock_osc_bridge.send_command.assert_any_call("/transport_play")

        assert result["success"] is True
        assert result["recording"] is True
        assert result["armed_tracks"] == [1, 3]  # Two armed tracks
        assert "2 armed track(s)" in result["message"]

    @pytest.mark.asyncio
    async def test_start_recording_not_connected(self, recording_tools, mock_osc_bridge):
        """Test start recording when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.start_recording()

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_recording_already_recording(self, recording_tools, mock_state):
        """Test start recording when already recording."""
        # Set transport state to recording
        mock_state.get_transport.return_value.recording = True

        result = await recording_tools.start_recording()

        assert result["success"] is False
        assert "Already recording" in result["error"]
        assert result["recording"] is True

    @pytest.mark.asyncio
    async def test_start_recording_rec_enable_fails(self, recording_tools, mock_osc_bridge):
        """Test start recording when rec_enable fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.start_recording()

        assert result["success"] is False
        assert "Failed to enable recording" in result["error"]

    @pytest.mark.asyncio
    async def test_start_recording_transport_play_fails(self, recording_tools, mock_osc_bridge):
        """Test start recording when transport_play fails with rollback."""
        # First call succeeds (rec_enable), second fails (transport_play), third is rollback
        mock_osc_bridge.send_command.side_effect = [True, False, True]

        result = await recording_tools.start_recording()

        assert result["success"] is False
        assert "Failed to start transport" in result["error"]
        # Should have called rec_enable_toggle twice (enable + rollback)
        assert mock_osc_bridge.send_command.call_count == 3

    @pytest.mark.asyncio
    async def test_start_recording_no_armed_tracks(self, recording_tools, mock_state, mock_osc_bridge):
        """Test start recording with no armed tracks (should warn but succeed)."""
        # Set all tracks to disarmed
        for track in mock_state.get_all_tracks.return_value.values():
            track.rec_enabled = False

        result = await recording_tools.start_recording()

        assert result["success"] is True
        assert result["armed_tracks"] == []
        assert "0 armed track(s)" in result["message"]


class TestStopRecording:
    """Test stop_recording method."""

    @pytest.mark.asyncio
    async def test_stop_recording_success(self, recording_tools, mock_osc_bridge, mock_state):
        """Test successfully stopping recording."""
        # Set state to recording
        mock_state.get_transport.return_value.recording = True

        result = await recording_tools.stop_recording()

        # Should send transport_stop and rec_enable_toggle
        assert mock_osc_bridge.send_command.call_count == 2
        mock_osc_bridge.send_command.assert_any_call("/transport_stop")
        mock_osc_bridge.send_command.assert_any_call("/rec_enable_toggle")

        assert result["success"] is True
        assert result["recording"] is False
        assert "Recording stopped" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_recording_not_connected(self, recording_tools, mock_osc_bridge):
        """Test stop recording when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.stop_recording()

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_stop_recording_when_not_recording(self, recording_tools, mock_osc_bridge, mock_state):
        """Test stop recording when not currently recording."""
        # Recording is False by default
        mock_state.get_transport.return_value.recording = False

        result = await recording_tools.stop_recording()

        # Should only send transport_stop, not rec_enable_toggle
        assert mock_osc_bridge.send_command.call_count == 1
        mock_osc_bridge.send_command.assert_called_once_with("/transport_stop")

        assert result["success"] is True
        assert result["recording"] is False

    @pytest.mark.asyncio
    async def test_stop_recording_transport_fails(self, recording_tools, mock_osc_bridge):
        """Test stop recording when transport_stop fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.stop_recording()

        assert result["success"] is False
        assert "Failed to stop transport" in result["error"]

    @pytest.mark.asyncio
    async def test_stop_recording_rec_disable_fails(self, recording_tools, mock_osc_bridge, mock_state):
        """Test stop recording when rec_enable_toggle fails."""
        mock_state.get_transport.return_value.recording = True
        # First call succeeds (transport_stop), second fails (rec_enable_toggle)
        mock_osc_bridge.send_command.side_effect = [True, False]

        result = await recording_tools.stop_recording()

        assert result["success"] is False
        assert "failed to disable recording mode" in result["error"]


class TestToggleRecording:
    """Test toggle_recording method."""

    @pytest.mark.asyncio
    async def test_toggle_recording_success(self, recording_tools, mock_osc_bridge):
        """Test successfully toggling recording."""
        result = await recording_tools.toggle_recording()

        mock_osc_bridge.send_command.assert_called_once_with("/rec_enable_toggle")
        assert result["success"] is True
        assert "recording" in result

    @pytest.mark.asyncio
    async def test_toggle_recording_not_connected(self, recording_tools, mock_osc_bridge):
        """Test toggle recording when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.toggle_recording()

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_toggle_recording_command_fails(self, recording_tools, mock_osc_bridge):
        """Test toggle recording when command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.toggle_recording()

        assert result["success"] is False
        assert "Failed to toggle recording" in result["error"]


class TestIsRecording:
    """Test is_recording query method."""

    @pytest.mark.asyncio
    async def test_is_recording_true(self, recording_tools, mock_state):
        """Test querying recording state when recording."""
        mock_state.get_transport.return_value.recording = True
        mock_state.get_transport.return_value.playing = True

        result = await recording_tools.is_recording()

        assert result["success"] is True
        assert result["recording"] is True
        assert result["playing"] is True
        assert result["armed_tracks"] == [1, 3]
        assert result["armed_count"] == 2

    @pytest.mark.asyncio
    async def test_is_recording_false(self, recording_tools, mock_state):
        """Test querying recording state when not recording."""
        mock_state.get_transport.return_value.recording = False
        mock_state.get_transport.return_value.playing = False

        result = await recording_tools.is_recording()

        assert result["success"] is True
        assert result["recording"] is False
        assert result["playing"] is False
        assert result["armed_count"] == 2

    @pytest.mark.asyncio
    async def test_is_recording_no_armed_tracks(self, recording_tools, mock_state):
        """Test querying recording state with no armed tracks."""
        # Disarm all tracks
        for track in mock_state.get_all_tracks.return_value.values():
            track.rec_enabled = False

        result = await recording_tools.is_recording()

        assert result["success"] is True
        assert result["armed_tracks"] == []
        assert result["armed_count"] == 0


class TestSetPunchRange:
    """Test set_punch_range method."""

    @pytest.mark.asyncio
    async def test_set_punch_range_success(self, recording_tools, mock_osc_bridge):
        """Test successfully setting punch range."""
        result = await recording_tools.set_punch_range(48000, 96000)

        # Should send both punch-in and punch-out commands
        assert mock_osc_bridge.send_command.call_count == 2
        mock_osc_bridge.send_command.assert_any_call("/set_punch_in", 48000)
        mock_osc_bridge.send_command.assert_any_call("/set_punch_out", 96000)

        assert result["success"] is True
        assert result["start_frame"] == 48000
        assert result["end_frame"] == 96000

    @pytest.mark.asyncio
    async def test_set_punch_range_not_connected(self, recording_tools, mock_osc_bridge):
        """Test set punch range when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.set_punch_range(48000, 96000)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_punch_range_invalid_start_negative(self, recording_tools, mock_osc_bridge):
        """Test set punch range with negative start frame."""
        result = await recording_tools.set_punch_range(-100, 96000)

        assert result["success"] is False
        assert "Invalid start_frame" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_punch_range_invalid_end_negative(self, recording_tools, mock_osc_bridge):
        """Test set punch range with negative end frame."""
        result = await recording_tools.set_punch_range(48000, -100)

        assert result["success"] is False
        assert "Invalid end_frame" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_punch_range_start_greater_than_end(self, recording_tools, mock_osc_bridge):
        """Test set punch range with start >= end."""
        result = await recording_tools.set_punch_range(96000, 48000)

        assert result["success"] is False
        assert "Invalid range" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_punch_range_start_equals_end(self, recording_tools, mock_osc_bridge):
        """Test set punch range with start == end."""
        result = await recording_tools.set_punch_range(48000, 48000)

        assert result["success"] is False
        assert "Invalid range" in result["error"]

    @pytest.mark.asyncio
    async def test_set_punch_range_punch_in_fails(self, recording_tools, mock_osc_bridge):
        """Test set punch range when punch-in command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.set_punch_range(48000, 96000)

        assert result["success"] is False
        assert "Failed to set punch-in point" in result["error"]

    @pytest.mark.asyncio
    async def test_set_punch_range_punch_out_fails(self, recording_tools, mock_osc_bridge):
        """Test set punch range when punch-out command fails."""
        # First call succeeds (punch-in), second fails (punch-out)
        mock_osc_bridge.send_command.side_effect = [True, False]

        result = await recording_tools.set_punch_range(48000, 96000)

        assert result["success"] is False
        assert "Failed to set punch-out point" in result["error"]

    @pytest.mark.asyncio
    async def test_set_punch_range_zero_start(self, recording_tools, mock_osc_bridge):
        """Test set punch range with zero start frame."""
        result = await recording_tools.set_punch_range(0, 96000)

        assert result["success"] is True
        assert result["start_frame"] == 0


class TestEnablePunchIn:
    """Test enable_punch_in method."""

    @pytest.mark.asyncio
    async def test_enable_punch_in_success(self, recording_tools, mock_osc_bridge):
        """Test successfully enabling punch-in."""
        result = await recording_tools.enable_punch_in()

        mock_osc_bridge.send_command.assert_called_once_with("/set_punch_in", 1)
        assert result["success"] is True
        assert "Punch-in enabled" in result["message"]

    @pytest.mark.asyncio
    async def test_enable_punch_in_not_connected(self, recording_tools, mock_osc_bridge):
        """Test enable punch-in when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.enable_punch_in()

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_enable_punch_in_command_fails(self, recording_tools, mock_osc_bridge):
        """Test enable punch-in when command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.enable_punch_in()

        assert result["success"] is False
        assert "Failed to enable punch-in" in result["error"]


class TestEnablePunchOut:
    """Test enable_punch_out method."""

    @pytest.mark.asyncio
    async def test_enable_punch_out_success(self, recording_tools, mock_osc_bridge):
        """Test successfully enabling punch-out."""
        result = await recording_tools.enable_punch_out()

        mock_osc_bridge.send_command.assert_called_once_with("/set_punch_out", 1)
        assert result["success"] is True
        assert "Punch-out enabled" in result["message"]

    @pytest.mark.asyncio
    async def test_enable_punch_out_not_connected(self, recording_tools, mock_osc_bridge):
        """Test enable punch-out when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.enable_punch_out()

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_enable_punch_out_command_fails(self, recording_tools, mock_osc_bridge):
        """Test enable punch-out when command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.enable_punch_out()

        assert result["success"] is False
        assert "Failed to enable punch-out" in result["error"]


class TestClearPunchRange:
    """Test clear_punch_range method."""

    @pytest.mark.asyncio
    async def test_clear_punch_range_success(self, recording_tools, mock_osc_bridge):
        """Test successfully clearing punch range."""
        result = await recording_tools.clear_punch_range()

        # Should disable both punch-in and punch-out
        assert mock_osc_bridge.send_command.call_count == 2
        mock_osc_bridge.send_command.assert_any_call("/set_punch_in", 0)
        mock_osc_bridge.send_command.assert_any_call("/set_punch_out", 0)

        assert result["success"] is True
        assert "Punch recording disabled" in result["message"]

    @pytest.mark.asyncio
    async def test_clear_punch_range_not_connected(self, recording_tools, mock_osc_bridge):
        """Test clear punch range when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.clear_punch_range()

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_clear_punch_range_punch_in_fails(self, recording_tools, mock_osc_bridge):
        """Test clear punch range when disabling punch-in fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.clear_punch_range()

        assert result["success"] is False
        assert "Failed to disable punch-in" in result["error"]

    @pytest.mark.asyncio
    async def test_clear_punch_range_punch_out_fails(self, recording_tools, mock_osc_bridge):
        """Test clear punch range when disabling punch-out fails."""
        # First call succeeds (punch-in), second fails (punch-out)
        mock_osc_bridge.send_command.side_effect = [True, False]

        result = await recording_tools.clear_punch_range()

        assert result["success"] is False
        assert "Failed to disable punch-out" in result["error"]


class TestSetInputMonitoring:
    """Test set_input_monitoring method."""

    @pytest.mark.asyncio
    async def test_set_input_monitoring_enable(self, recording_tools, mock_osc_bridge):
        """Test enabling input monitoring."""
        result = await recording_tools.set_input_monitoring(1, True)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/monitor_input", 1, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["input_monitoring"] is True

    @pytest.mark.asyncio
    async def test_set_input_monitoring_disable(self, recording_tools, mock_osc_bridge):
        """Test disabling input monitoring."""
        result = await recording_tools.set_input_monitoring(1, False)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/monitor_input", 1, 0)
        assert result["success"] is True
        assert result["input_monitoring"] is False

    @pytest.mark.asyncio
    async def test_set_input_monitoring_not_connected(self, recording_tools, mock_osc_bridge):
        """Test set input monitoring when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.set_input_monitoring(1, True)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_input_monitoring_track_not_found(self, recording_tools):
        """Test set input monitoring with invalid track ID."""
        result = await recording_tools.set_input_monitoring(99, True)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_set_input_monitoring_command_fails(self, recording_tools, mock_osc_bridge):
        """Test set input monitoring when command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.set_input_monitoring(1, True)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestSetDiskMonitoring:
    """Test set_disk_monitoring method."""

    @pytest.mark.asyncio
    async def test_set_disk_monitoring_enable(self, recording_tools, mock_osc_bridge):
        """Test enabling disk monitoring."""
        result = await recording_tools.set_disk_monitoring(1, True)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/monitor_disk", 1, 1)
        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["disk_monitoring"] is True

    @pytest.mark.asyncio
    async def test_set_disk_monitoring_disable(self, recording_tools, mock_osc_bridge):
        """Test disabling disk monitoring."""
        result = await recording_tools.set_disk_monitoring(1, False)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/monitor_disk", 1, 0)
        assert result["success"] is True
        assert result["disk_monitoring"] is False

    @pytest.mark.asyncio
    async def test_set_disk_monitoring_not_connected(self, recording_tools, mock_osc_bridge):
        """Test set disk monitoring when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.set_disk_monitoring(1, True)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_disk_monitoring_track_not_found(self, recording_tools):
        """Test set disk monitoring with invalid track ID."""
        result = await recording_tools.set_disk_monitoring(99, True)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_set_disk_monitoring_command_fails(self, recording_tools, mock_osc_bridge):
        """Test set disk monitoring when command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.set_disk_monitoring(1, True)

        assert result["success"] is False
        assert "Failed to send OSC command" in result["error"]


class TestSetMonitoringMode:
    """Test set_monitoring_mode method."""

    @pytest.mark.asyncio
    async def test_set_monitoring_mode_input(self, recording_tools, mock_osc_bridge):
        """Test setting monitoring mode to input."""
        result = await recording_tools.set_monitoring_mode(1, "input")

        # Should enable input, disable disk
        assert mock_osc_bridge.send_command.call_count == 2
        mock_osc_bridge.send_command.assert_any_call("/strip/monitor_input", 1, 1)
        mock_osc_bridge.send_command.assert_any_call("/strip/monitor_disk", 1, 0)

        assert result["success"] is True
        assert result["mode"] == "input"

    @pytest.mark.asyncio
    async def test_set_monitoring_mode_disk(self, recording_tools, mock_osc_bridge):
        """Test setting monitoring mode to disk."""
        result = await recording_tools.set_monitoring_mode(1, "disk")

        # Should disable input, enable disk
        assert mock_osc_bridge.send_command.call_count == 2
        mock_osc_bridge.send_command.assert_any_call("/strip/monitor_input", 1, 0)
        mock_osc_bridge.send_command.assert_any_call("/strip/monitor_disk", 1, 1)

        assert result["success"] is True
        assert result["mode"] == "disk"

    @pytest.mark.asyncio
    async def test_set_monitoring_mode_auto(self, recording_tools, mock_osc_bridge):
        """Test setting monitoring mode to auto."""
        result = await recording_tools.set_monitoring_mode(1, "auto")

        # Should disable both to let Ardour manage
        assert mock_osc_bridge.send_command.call_count == 2
        mock_osc_bridge.send_command.assert_any_call("/strip/monitor_input", 1, 0)
        mock_osc_bridge.send_command.assert_any_call("/strip/monitor_disk", 1, 0)

        assert result["success"] is True
        assert result["mode"] == "auto"

    @pytest.mark.asyncio
    async def test_set_monitoring_mode_case_insensitive(self, recording_tools, mock_osc_bridge):
        """Test setting monitoring mode with uppercase input."""
        result = await recording_tools.set_monitoring_mode(1, "INPUT")

        assert result["success"] is True
        assert result["mode"] == "input"

    @pytest.mark.asyncio
    async def test_set_monitoring_mode_invalid(self, recording_tools, mock_osc_bridge):
        """Test setting monitoring mode with invalid mode."""
        result = await recording_tools.set_monitoring_mode(1, "invalid")

        assert result["success"] is False
        assert "Invalid mode" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_monitoring_mode_not_connected(self, recording_tools, mock_osc_bridge):
        """Test set monitoring mode when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await recording_tools.set_monitoring_mode(1, "input")

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_monitoring_mode_track_not_found(self, recording_tools):
        """Test set monitoring mode with invalid track ID."""
        result = await recording_tools.set_monitoring_mode(99, "input")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_set_monitoring_mode_command_fails(self, recording_tools, mock_osc_bridge):
        """Test set monitoring mode when command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await recording_tools.set_monitoring_mode(1, "input")

        assert result["success"] is False
        assert "Failed to set monitoring mode" in result["error"]


class TestGetArmedTracks:
    """Test get_armed_tracks query method."""

    @pytest.mark.asyncio
    async def test_get_armed_tracks_with_armed(self, recording_tools):
        """Test getting armed tracks when tracks are armed."""
        result = await recording_tools.get_armed_tracks()

        assert result["success"] is True
        assert result["armed_count"] == 2
        assert len(result["armed_tracks"]) == 2

        # Check the armed tracks details
        armed_ids = [track["track_id"] for track in result["armed_tracks"]]
        assert 1 in armed_ids  # Vocals
        assert 3 in armed_ids  # Bass

    @pytest.mark.asyncio
    async def test_get_armed_tracks_none_armed(self, recording_tools, mock_state):
        """Test getting armed tracks when no tracks are armed."""
        # Disarm all tracks
        for track in mock_state.get_all_tracks.return_value.values():
            track.rec_enabled = False

        result = await recording_tools.get_armed_tracks()

        assert result["success"] is True
        assert result["armed_count"] == 0
        assert result["armed_tracks"] == []

    @pytest.mark.asyncio
    async def test_get_armed_tracks_details(self, recording_tools):
        """Test armed tracks return correct details."""
        result = await recording_tools.get_armed_tracks()

        # Check first armed track details
        track1 = next(t for t in result["armed_tracks"] if t["track_id"] == 1)
        assert track1["name"] == "Vocals"
        assert track1["type"] == "audio"


class TestGetRecordingState:
    """Test get_recording_state query method."""

    @pytest.mark.asyncio
    async def test_get_recording_state_recording(self, recording_tools, mock_state):
        """Test getting recording state when recording."""
        mock_state.get_transport.return_value.recording = True
        mock_state.get_transport.return_value.playing = True
        mock_state.get_transport.return_value.frame = 48000
        mock_state.get_transport.return_value.tempo = 140.0

        result = await recording_tools.get_recording_state()

        assert result["success"] is True
        assert result["recording"] is True
        assert result["playing"] is True
        assert result["armed_count"] == 2
        assert result["armed_tracks"] == [1, 3]
        assert result["tempo"] == 140.0
        assert result["frame"] == 48000

    @pytest.mark.asyncio
    async def test_get_recording_state_not_recording(self, recording_tools, mock_state):
        """Test getting recording state when not recording."""
        result = await recording_tools.get_recording_state()

        assert result["success"] is True
        assert result["recording"] is False
        assert result["playing"] is False

    @pytest.mark.asyncio
    async def test_get_recording_state_no_armed_tracks(self, recording_tools, mock_state):
        """Test getting recording state with no armed tracks."""
        # Disarm all tracks
        for track in mock_state.get_all_tracks.return_value.values():
            track.rec_enabled = False

        result = await recording_tools.get_recording_state()

        assert result["success"] is True
        assert result["armed_count"] == 0
        assert result["armed_tracks"] == []
