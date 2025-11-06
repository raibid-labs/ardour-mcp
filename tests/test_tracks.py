"""
Tests for track management tools.

Tests all track-related MCP tools.
"""

from unittest.mock import Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, TrackState
from ardour_mcp.tools.tracks import TrackTools


@pytest.fixture
def mock_osc_bridge():
    """Create a mock OSC bridge for testing."""
    bridge = Mock()
    bridge.is_connected.return_value = True
    bridge.send_command.return_value = True
    return bridge


@pytest.fixture
def mock_state():
    """Create a mock state with some test tracks."""
    state = Mock(spec=ArdourState)

    # Create sample tracks
    track1 = TrackState(strip_id=1, name="Audio 1", track_type="audio")
    track2 = TrackState(strip_id=2, name="MIDI 1", track_type="midi", muted=True)
    track3 = TrackState(strip_id=3, name="Vocals", track_type="audio", gain_db=-6.0, pan=0.5)

    state.get_all_tracks.return_value = {
        1: track1,
        2: track2,
        3: track3,
    }
    state.get_track.side_effect = lambda track_id: {
        1: track1,
        2: track2,
        3: track3,
    }.get(track_id)

    return state


@pytest.fixture
def track_tools(mock_osc_bridge, mock_state):
    """Create TrackTools instance with mocked dependencies."""
    return TrackTools(mock_osc_bridge, mock_state)


class TestTrackToolsInitialization:
    """Test TrackTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of TrackTools."""
        tools = TrackTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state


class TestCreateAudioTrack:
    """Test creating audio tracks."""

    @pytest.mark.asyncio
    async def test_create_audio_track_success(self, track_tools, mock_osc_bridge, mock_state):
        """Test successfully creating an audio track."""
        result = await track_tools.create_audio_track("Vocals")

        # Verify OSC command was sent
        mock_osc_bridge.send_command.assert_called_once_with("/add_audio_track", 1)

        # Verify result
        assert result["success"] is True
        assert "Vocals" in result["message"]
        assert "track_count" in result

    @pytest.mark.asyncio
    async def test_create_audio_track_without_name(self, track_tools, mock_osc_bridge):
        """Test creating an audio track without specifying a name."""
        result = await track_tools.create_audio_track()

        mock_osc_bridge.send_command.assert_called_once_with("/add_audio_track", 1)
        assert result["success"] is True
        assert "Created audio track" in result["message"]

    @pytest.mark.asyncio
    async def test_create_audio_track_not_connected(self, track_tools, mock_osc_bridge):
        """Test creating audio track when not connected to Ardour."""
        mock_osc_bridge.is_connected.return_value = False

        result = await track_tools.create_audio_track("Test")

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_audio_track_command_fails(self, track_tools, mock_osc_bridge):
        """Test handling OSC command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await track_tools.create_audio_track("Test")

        assert result["success"] is False
        assert "error" in result


class TestCreateMidiTrack:
    """Test creating MIDI tracks."""

    @pytest.mark.asyncio
    async def test_create_midi_track_success(self, track_tools, mock_osc_bridge):
        """Test successfully creating a MIDI track."""
        result = await track_tools.create_midi_track("Piano")

        mock_osc_bridge.send_command.assert_called_once_with("/add_midi_track", 1)
        assert result["success"] is True
        assert "Piano" in result["message"]

    @pytest.mark.asyncio
    async def test_create_midi_track_without_name(self, track_tools, mock_osc_bridge):
        """Test creating a MIDI track without specifying a name."""
        result = await track_tools.create_midi_track()

        mock_osc_bridge.send_command.assert_called_once_with("/add_midi_track", 1)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_create_midi_track_not_connected(self, track_tools, mock_osc_bridge):
        """Test creating MIDI track when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await track_tools.create_midi_track("Test")

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_create_midi_track_command_fails(self, track_tools, mock_osc_bridge):
        """Test handling OSC command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await track_tools.create_midi_track("Test")

        assert result["success"] is False


class TestListTracks:
    """Test listing tracks."""

    @pytest.mark.asyncio
    async def test_list_tracks_with_data(self, track_tools, mock_state):
        """Test listing tracks when tracks exist."""
        result = await track_tools.list_tracks()

        assert result["success"] is True
        assert result["track_count"] == 3
        assert len(result["tracks"]) == 3

        # Verify track data structure
        track = result["tracks"][0]
        assert "strip_id" in track
        assert "name" in track
        assert "type" in track
        assert "muted" in track
        assert "soloed" in track
        assert "rec_enabled" in track
        assert "gain_db" in track
        assert "pan" in track

    @pytest.mark.asyncio
    async def test_list_tracks_empty(self, track_tools, mock_state):
        """Test listing tracks when no tracks exist."""
        mock_state.get_all_tracks.return_value = {}

        result = await track_tools.list_tracks()

        assert result["success"] is True
        assert result["track_count"] == 0
        assert result["tracks"] == []

    @pytest.mark.asyncio
    async def test_list_tracks_sorted(self, track_tools, mock_state):
        """Test that tracks are returned in sorted order by strip_id."""
        result = await track_tools.list_tracks()

        strip_ids = [track["strip_id"] for track in result["tracks"]]
        assert strip_ids == sorted(strip_ids)

    @pytest.mark.asyncio
    async def test_list_tracks_includes_all_properties(self, track_tools):
        """Test that all track properties are included."""
        result = await track_tools.list_tracks()

        # Check the "Vocals" track (strip_id=3)
        vocals_track = next(t for t in result["tracks"] if t["name"] == "Vocals")
        assert vocals_track["strip_id"] == 3
        assert vocals_track["type"] == "audio"
        assert vocals_track["gain_db"] == -6.0
        assert vocals_track["pan"] == 0.5


class TestSelectTrack:
    """Test selecting tracks."""

    @pytest.mark.asyncio
    async def test_select_track_success(self, track_tools, mock_osc_bridge):
        """Test successfully selecting a track."""
        result = await track_tools.select_track(2)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/select", 2, 1)
        assert result["success"] is True
        assert result["track_id"] == 2
        assert "MIDI 1" in result["track_name"]

    @pytest.mark.asyncio
    async def test_select_track_unknown(self, track_tools, mock_osc_bridge, mock_state):
        """Test selecting a track that doesn't exist in state."""
        mock_state.get_track.return_value = None

        result = await track_tools.select_track(99)

        mock_osc_bridge.send_command.assert_called_once_with("/strip/select", 99, 1)
        assert result["success"] is True
        assert result["track_name"] == "Unknown"

    @pytest.mark.asyncio
    async def test_select_track_invalid_id(self, track_tools, mock_osc_bridge):
        """Test selecting track with invalid ID."""
        result = await track_tools.select_track(0)

        assert result["success"] is False
        assert "positive" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_select_track_negative_id(self, track_tools, mock_osc_bridge):
        """Test selecting track with negative ID."""
        result = await track_tools.select_track(-1)

        assert result["success"] is False
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_select_track_not_connected(self, track_tools, mock_osc_bridge):
        """Test selecting track when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await track_tools.select_track(1)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_select_track_command_fails(self, track_tools, mock_osc_bridge):
        """Test handling OSC command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await track_tools.select_track(1)

        assert result["success"] is False


class TestRenameTrack:
    """Test renaming tracks."""

    @pytest.mark.asyncio
    async def test_rename_track_success(self, track_tools, mock_osc_bridge):
        """Test successfully renaming a track."""
        result = await track_tools.rename_track(3, "Lead Vocals")

        mock_osc_bridge.send_command.assert_called_once_with("/strip/name", 3, "Lead Vocals")
        assert result["success"] is True
        assert result["track_id"] == 3
        assert result["old_name"] == "Vocals"
        assert result["new_name"] == "Lead Vocals"

    @pytest.mark.asyncio
    async def test_rename_track_unknown(self, track_tools, mock_osc_bridge, mock_state):
        """Test renaming a track that doesn't exist in state."""
        mock_state.get_track.return_value = None

        result = await track_tools.rename_track(99, "New Name")

        mock_osc_bridge.send_command.assert_called_once()
        assert result["success"] is True
        assert result["old_name"] == "Unknown"

    @pytest.mark.asyncio
    async def test_rename_track_invalid_id(self, track_tools, mock_osc_bridge):
        """Test renaming track with invalid ID."""
        result = await track_tools.rename_track(0, "Test")

        assert result["success"] is False
        assert "positive" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_rename_track_empty_name(self, track_tools, mock_osc_bridge):
        """Test renaming track with empty name."""
        result = await track_tools.rename_track(1, "")

        assert result["success"] is False
        assert "empty" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_rename_track_whitespace_name(self, track_tools, mock_osc_bridge):
        """Test renaming track with whitespace-only name."""
        result = await track_tools.rename_track(1, "   ")

        assert result["success"] is False
        assert "empty" in result["error"]

    @pytest.mark.asyncio
    async def test_rename_track_not_connected(self, track_tools, mock_osc_bridge):
        """Test renaming track when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await track_tools.rename_track(1, "Test")

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_rename_track_command_fails(self, track_tools, mock_osc_bridge):
        """Test handling OSC command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await track_tools.rename_track(1, "New Name")

        assert result["success"] is False


class TestTrackToolsIntegration:
    """Integration tests for track tools."""

    @pytest.mark.asyncio
    async def test_create_and_list_workflow(self, track_tools, mock_osc_bridge, mock_state):
        """Test creating a track and then listing all tracks."""
        # Create track
        create_result = await track_tools.create_audio_track("New Track")
        assert create_result["success"] is True

        # List tracks
        list_result = await track_tools.list_tracks()
        assert list_result["success"] is True
        assert list_result["track_count"] == 3

    @pytest.mark.asyncio
    async def test_create_select_rename_workflow(self, track_tools, mock_osc_bridge):
        """Test creating, selecting, and renaming a track."""
        # Create
        await track_tools.create_audio_track()
        assert mock_osc_bridge.send_command.called

        # Select
        mock_osc_bridge.reset_mock()
        await track_tools.select_track(1)
        assert mock_osc_bridge.send_command.called

        # Rename
        mock_osc_bridge.reset_mock()
        result = await track_tools.rename_track(1, "Final Name")
        assert result["success"] is True
