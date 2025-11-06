"""
Tests for session information tools.

Tests all session-related MCP tools.
"""

from unittest.mock import Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, SessionState, TransportState
from ardour_mcp.tools.session import SessionTools


@pytest.fixture
def mock_osc_bridge():
    """Create a mock OSC bridge for testing."""
    bridge = Mock()
    bridge.is_connected.return_value = True
    bridge.send_command.return_value = True
    return bridge


@pytest.fixture
def mock_state():
    """Create a mock state with session information."""
    state = Mock(spec=ArdourState)

    transport = TransportState(
        playing=False,
        recording=False,
        frame=0,
        tempo=120.0,
        time_signature=(4, 4),
        loop_enabled=False
    )

    session = SessionState(
        name="Test Session",
        path="/home/user/Test Session.ardour",
        sample_rate=48000,
        tracks={},
        markers=[("Intro", 0), ("Verse", 96000), ("Chorus", 192000)],
        transport=transport,
        dirty=False
    )

    state.get_session_info.return_value = session
    state.get_transport.return_value = transport
    state.get_all_tracks.return_value = {}

    return state


@pytest.fixture
def session_tools(mock_osc_bridge, mock_state):
    """Create SessionTools instance with mocked dependencies."""
    return SessionTools(mock_osc_bridge, mock_state)


class TestSessionToolsInitialization:
    """Test SessionTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of SessionTools."""
        tools = SessionTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state


class TestGetSessionInfo:
    """Test getting complete session information."""

    @pytest.mark.asyncio
    async def test_get_session_info_success(self, session_tools):
        """Test successfully getting session information."""
        result = await session_tools.get_session_info()

        assert result["success"] is True
        assert result["session_name"] == "Test Session"
        assert result["session_path"] == "/home/user/Test Session.ardour"
        assert result["sample_rate"] == 48000
        assert result["tempo"] == 120.0
        assert result["time_signature"] == "4/4"
        assert result["track_count"] == 0
        assert result["marker_count"] == 3
        assert result["dirty"] is False
        assert result["playing"] is False
        assert result["recording"] is False
        assert result["frame"] == 0


class TestGetTempo:
    """Test getting session tempo."""

    @pytest.mark.asyncio
    async def test_get_tempo_success(self, session_tools):
        """Test successfully getting tempo."""
        result = await session_tools.get_tempo()

        assert result["success"] is True
        assert result["tempo"] == 120.0
        assert "120" in result["message"]


class TestGetTimeSignature:
    """Test getting time signature."""

    @pytest.mark.asyncio
    async def test_get_time_signature_success(self, session_tools):
        """Test successfully getting time signature."""
        result = await session_tools.get_time_signature()

        assert result["success"] is True
        assert result["time_signature"] == "4/4"
        assert result["beats_per_bar"] == 4
        assert result["beat_type"] == 4
        assert "4/4" in result["message"]

    @pytest.mark.asyncio
    async def test_get_time_signature_complex(self, session_tools, mock_state):
        """Test getting complex time signature."""
        transport = mock_state.get_transport.return_value
        transport.time_signature = (7, 8)

        result = await session_tools.get_time_signature()

        assert result["time_signature"] == "7/8"
        assert result["beats_per_bar"] == 7
        assert result["beat_type"] == 8


class TestGetSampleRate:
    """Test getting sample rate."""

    @pytest.mark.asyncio
    async def test_get_sample_rate_success(self, session_tools):
        """Test successfully getting sample rate."""
        result = await session_tools.get_sample_rate()

        assert result["success"] is True
        assert result["sample_rate"] == 48000
        assert "48000" in result["message"]

    @pytest.mark.asyncio
    async def test_get_sample_rate_44100(self, session_tools, mock_state):
        """Test getting 44.1kHz sample rate."""
        session = mock_state.get_session_info.return_value
        session.sample_rate = 44100

        result = await session_tools.get_sample_rate()

        assert result["sample_rate"] == 44100


class TestListMarkers:
    """Test listing markers."""

    @pytest.mark.asyncio
    async def test_list_markers_success(self, session_tools):
        """Test successfully listing markers."""
        result = await session_tools.list_markers()

        assert result["success"] is True
        assert result["marker_count"] == 3
        assert len(result["markers"]) == 3

        # Check marker structure
        markers = result["markers"]
        assert markers[0] == {"name": "Intro", "frame": 0}
        assert markers[1] == {"name": "Verse", "frame": 96000}
        assert markers[2] == {"name": "Chorus", "frame": 192000}

    @pytest.mark.asyncio
    async def test_list_markers_empty(self, session_tools, mock_state):
        """Test listing markers when none exist."""
        session = mock_state.get_session_info.return_value
        session.markers = []

        result = await session_tools.list_markers()

        assert result["success"] is True
        assert result["marker_count"] == 0
        assert result["markers"] == []


class TestSaveSession:
    """Test saving session."""

    @pytest.mark.asyncio
    async def test_save_session_success(self, session_tools, mock_osc_bridge):
        """Test successfully saving session."""
        result = await session_tools.save_session()

        mock_osc_bridge.send_command.assert_called_once_with("/save_state")
        assert result["success"] is True
        assert "saved" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_save_session_not_connected(self, session_tools, mock_osc_bridge):
        """Test saving session when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await session_tools.save_session()

        assert result["success"] is False
        assert "Not connected" in result["error"]
        mock_osc_bridge.send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_session_command_fails(self, session_tools, mock_osc_bridge):
        """Test handling save command failure."""
        mock_osc_bridge.send_command.return_value = False

        result = await session_tools.save_session()

        assert result["success"] is False
        assert "failed" in result["message"].lower()


class TestGetTrackCount:
    """Test getting track count."""

    @pytest.mark.asyncio
    async def test_get_track_count_zero(self, session_tools):
        """Test getting track count when no tracks exist."""
        result = await session_tools.get_track_count()

        assert result["success"] is True
        assert result["track_count"] == 0
        assert "0" in result["message"]

    @pytest.mark.asyncio
    async def test_get_track_count_multiple(self, session_tools, mock_state):
        """Test getting track count with multiple tracks."""
        mock_state.get_all_tracks.return_value = {
            1: Mock(),
            2: Mock(),
            3: Mock(),
        }

        result = await session_tools.get_track_count()

        assert result["track_count"] == 3
        assert "3" in result["message"]


class TestIsSessionDirty:
    """Test checking session dirty state."""

    @pytest.mark.asyncio
    async def test_is_session_dirty_false(self, session_tools):
        """Test when session is clean (saved)."""
        result = await session_tools.is_session_dirty()

        assert result["success"] is True
        assert result["dirty"] is False
        assert "saved" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_is_session_dirty_true(self, session_tools, mock_state):
        """Test when session has unsaved changes."""
        session = mock_state.get_session_info.return_value
        session.dirty = True

        result = await session_tools.is_session_dirty()

        assert result["dirty"] is True
        assert "unsaved" in result["message"].lower()


class TestSessionToolsIntegration:
    """Integration tests for session tools."""

    @pytest.mark.asyncio
    async def test_get_info_and_save_workflow(self, session_tools, mock_osc_bridge, mock_state):
        """Test getting session info and saving."""
        # Get info
        info_result = await session_tools.get_session_info()
        assert info_result["success"] is True

        # Mark as dirty
        session = mock_state.get_session_info.return_value
        session.dirty = True

        # Check dirty
        dirty_result = await session_tools.is_session_dirty()
        assert dirty_result["dirty"] is True

        # Save
        save_result = await session_tools.save_session()
        assert save_result["success"] is True

    @pytest.mark.asyncio
    async def test_query_all_session_details(self, session_tools):
        """Test querying all session details."""
        # Get complete info
        info = await session_tools.get_session_info()
        assert info["success"] is True

        # Get individual components
        tempo = await session_tools.get_tempo()
        assert tempo["tempo"] == info["tempo"]

        time_sig = await session_tools.get_time_signature()
        assert time_sig["time_signature"] == info["time_signature"]

        sample_rate = await session_tools.get_sample_rate()
        assert sample_rate["sample_rate"] == info["sample_rate"]

        markers = await session_tools.list_markers()
        assert markers["marker_count"] == info["marker_count"]

        tracks = await session_tools.get_track_count()
        assert tracks["track_count"] == info["track_count"]
