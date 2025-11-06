"""
Tests for navigation control tools.

Tests all navigation-related MCP tools including marker management,
loop control, tempo/time signature, and navigation helpers.
"""

from unittest.mock import Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, SessionState, TransportState
from ardour_mcp.tools.navigation import NavigationTools


@pytest.fixture
def mock_osc_bridge():
    """Create a mock OSC bridge for testing."""
    bridge = Mock()
    bridge.is_connected.return_value = True
    bridge.send_command.return_value = True
    return bridge


@pytest.fixture
def mock_state():
    """Create a mock state with sample session data."""
    state = Mock(spec=ArdourState)

    # Create transport state
    transport = TransportState(
        playing=False,
        recording=False,
        frame=48000,
        tempo=120.0,
        time_signature=(4, 4),
        loop_enabled=False,
    )

    # Create session state with markers
    session = SessionState(
        name="Test Session",
        path="/path/to/session",
        sample_rate=48000,
        markers=[
            ("Intro", 0),
            ("Verse 1", 96000),
            ("Chorus", 240000),
            ("Verse 2", 384000),
            ("Outro", 528000),
        ],
        transport=transport,
    )

    state.get_transport.return_value = transport
    state.get_session_info.return_value = session

    return state


@pytest.fixture
def navigation_tools(mock_osc_bridge, mock_state):
    """Create NavigationTools instance with mocked dependencies."""
    return NavigationTools(mock_osc_bridge, mock_state)


class TestNavigationToolsInitialization:
    """Test NavigationTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of NavigationTools."""
        tools = NavigationTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state


# ==================== Marker Management Tests ====================


class TestCreateMarker:
    """Test marker creation."""

    @pytest.mark.asyncio
    async def test_create_marker_at_current_position(self, navigation_tools, mock_osc_bridge):
        """Test creating marker at current position."""
        result = await navigation_tools.create_marker("Test Marker")

        mock_osc_bridge.send_command.assert_called_once_with("/add_marker", "Test Marker")
        assert result["success"] is True
        assert result["marker_name"] == "Test Marker"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_create_marker_at_specific_position(
        self, navigation_tools, mock_osc_bridge
    ):
        """Test creating marker at specific position."""
        result = await navigation_tools.create_marker("Test Marker", 96000)

        # Should call locate first, then add_marker
        assert mock_osc_bridge.send_command.call_count == 2
        mock_osc_bridge.send_command.assert_any_call("/locate", 96000, 1)
        mock_osc_bridge.send_command.assert_any_call("/add_marker", "Test Marker")
        assert result["success"] is True
        assert result["marker_name"] == "Test Marker"
        assert result["position"] == 96000

    @pytest.mark.asyncio
    async def test_create_marker_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test create marker when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.create_marker("Test Marker")

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_create_marker_empty_name(self, navigation_tools):
        """Test create marker with empty name."""
        result = await navigation_tools.create_marker("")

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_create_marker_negative_position(self, navigation_tools):
        """Test create marker with negative position."""
        result = await navigation_tools.create_marker("Test", -100)

        assert result["success"] is False
        assert "non-negative" in result["error"]

    @pytest.mark.asyncio
    async def test_create_marker_locate_fails(self, navigation_tools, mock_osc_bridge):
        """Test create marker when locate fails."""
        mock_osc_bridge.send_command.side_effect = [False, True]

        result = await navigation_tools.create_marker("Test", 96000)

        assert result["success"] is False
        assert "Failed to locate" in result["error"]


class TestDeleteMarker:
    """Test marker deletion."""

    @pytest.mark.asyncio
    async def test_delete_marker_success(self, navigation_tools, mock_osc_bridge):
        """Test successfully deleting a marker."""
        result = await navigation_tools.delete_marker("Verse 1")

        mock_osc_bridge.send_command.assert_called_once_with("/remove_marker", "Verse 1")
        assert result["success"] is True
        assert result["marker_name"] == "Verse 1"

    @pytest.mark.asyncio
    async def test_delete_marker_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test delete marker when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.delete_marker("Verse 1")

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_delete_marker_empty_name(self, navigation_tools):
        """Test delete marker with empty name."""
        result = await navigation_tools.delete_marker("")

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_delete_marker_fails(self, navigation_tools, mock_osc_bridge):
        """Test delete marker when OSC command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await navigation_tools.delete_marker("Verse 1")

        assert result["success"] is False
        assert "Failed to delete" in result["error"]


class TestRenameMarker:
    """Test marker renaming."""

    @pytest.mark.asyncio
    async def test_rename_marker_success(self, navigation_tools, mock_osc_bridge):
        """Test successfully renaming a marker."""
        result = await navigation_tools.rename_marker("Verse 1", "Verse 1A")

        # Should get position, delete old, locate to position, create new
        # That's 3 calls: /remove_marker, /locate, /add_marker
        assert mock_osc_bridge.send_command.call_count == 3
        mock_osc_bridge.send_command.assert_any_call("/remove_marker", "Verse 1")
        mock_osc_bridge.send_command.assert_any_call("/locate", 96000, 1)
        mock_osc_bridge.send_command.assert_any_call("/add_marker", "Verse 1A")
        assert result["success"] is True
        assert result["old_name"] == "Verse 1"
        assert result["new_name"] == "Verse 1A"

    @pytest.mark.asyncio
    async def test_rename_marker_not_found(self, navigation_tools):
        """Test rename marker when marker doesn't exist."""
        result = await navigation_tools.rename_marker("Nonexistent", "New Name")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_rename_marker_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test rename marker when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.rename_marker("Verse 1", "Verse 1A")

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_rename_marker_empty_old_name(self, navigation_tools):
        """Test rename marker with empty old name."""
        result = await navigation_tools.rename_marker("", "New Name")

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_rename_marker_empty_new_name(self, navigation_tools):
        """Test rename marker with empty new name."""
        result = await navigation_tools.rename_marker("Verse 1", "")

        assert result["success"] is False
        assert "empty" in result["error"].lower()


class TestGotoMarker:
    """Test jumping to markers."""

    @pytest.mark.asyncio
    async def test_goto_marker_success(self, navigation_tools, mock_osc_bridge):
        """Test successfully jumping to a marker."""
        result = await navigation_tools.goto_marker("Chorus")

        mock_osc_bridge.send_command.assert_called_once_with("/locate", "Chorus")
        assert result["success"] is True
        assert result["marker_name"] == "Chorus"

    @pytest.mark.asyncio
    async def test_goto_marker_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test goto marker when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.goto_marker("Chorus")

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_goto_marker_empty_name(self, navigation_tools):
        """Test goto marker with empty name."""
        result = await navigation_tools.goto_marker("")

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_goto_marker_fails(self, navigation_tools, mock_osc_bridge):
        """Test goto marker when OSC command fails."""
        mock_osc_bridge.send_command.return_value = False

        result = await navigation_tools.goto_marker("Chorus")

        assert result["success"] is False
        assert "Failed to jump" in result["error"]


class TestGetMarkerPosition:
    """Test querying marker positions."""

    @pytest.mark.asyncio
    async def test_get_marker_position_success(self, navigation_tools):
        """Test successfully getting marker position."""
        result = await navigation_tools.get_marker_position("Verse 1")

        assert result["success"] is True
        assert result["marker_name"] == "Verse 1"
        assert result["position"] == 96000

    @pytest.mark.asyncio
    async def test_get_marker_position_not_found(self, navigation_tools):
        """Test get marker position for nonexistent marker."""
        result = await navigation_tools.get_marker_position("Nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_marker_position_empty_name(self, navigation_tools):
        """Test get marker position with empty name."""
        result = await navigation_tools.get_marker_position("")

        assert result["success"] is False
        assert "empty" in result["error"].lower()


# ==================== Loop Control Tests ====================


class TestSetLoopRange:
    """Test loop range setting."""

    @pytest.mark.asyncio
    async def test_set_loop_range_success(self, navigation_tools, mock_osc_bridge):
        """Test successfully setting loop range."""
        result = await navigation_tools.set_loop_range(48000, 96000)

        mock_osc_bridge.send_command.assert_called_once_with(
            "/set_loop_range", 48000, 96000
        )
        assert result["success"] is True
        assert result["loop_start"] == 48000
        assert result["loop_end"] == 96000

    @pytest.mark.asyncio
    async def test_set_loop_range_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test set loop range when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.set_loop_range(48000, 96000)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_loop_range_negative_frames(self, navigation_tools):
        """Test set loop range with negative frames."""
        result = await navigation_tools.set_loop_range(-100, 96000)

        assert result["success"] is False
        assert "non-negative" in result["error"]

    @pytest.mark.asyncio
    async def test_set_loop_range_end_before_start(self, navigation_tools):
        """Test set loop range with end before start."""
        result = await navigation_tools.set_loop_range(96000, 48000)

        assert result["success"] is False
        assert "after start" in result["error"]


class TestEnableLoop:
    """Test enabling loop."""

    @pytest.mark.asyncio
    async def test_enable_loop_success(self, navigation_tools, mock_osc_bridge, mock_state):
        """Test successfully enabling loop."""
        # Start with loop disabled
        transport = mock_state.get_transport.return_value
        transport.loop_enabled = False

        result = await navigation_tools.enable_loop()

        mock_osc_bridge.send_command.assert_called_once_with("/loop_toggle")
        assert result["success"] is True
        assert result["loop_enabled"] is True

    @pytest.mark.asyncio
    async def test_enable_loop_already_enabled(
        self, navigation_tools, mock_osc_bridge, mock_state
    ):
        """Test enable loop when already enabled."""
        # Start with loop enabled
        transport = mock_state.get_transport.return_value
        transport.loop_enabled = True

        result = await navigation_tools.enable_loop()

        # Should not toggle
        mock_osc_bridge.send_command.assert_not_called()
        assert result["success"] is True
        assert result["loop_enabled"] is True

    @pytest.mark.asyncio
    async def test_enable_loop_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test enable loop when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.enable_loop()

        assert result["success"] is False
        assert "Not connected" in result["error"]


class TestDisableLoop:
    """Test disabling loop."""

    @pytest.mark.asyncio
    async def test_disable_loop_success(
        self, navigation_tools, mock_osc_bridge, mock_state
    ):
        """Test successfully disabling loop."""
        # Start with loop enabled
        transport = mock_state.get_transport.return_value
        transport.loop_enabled = True

        result = await navigation_tools.disable_loop()

        mock_osc_bridge.send_command.assert_called_once_with("/loop_toggle")
        assert result["success"] is True
        assert result["loop_enabled"] is False

    @pytest.mark.asyncio
    async def test_disable_loop_already_disabled(
        self, navigation_tools, mock_osc_bridge, mock_state
    ):
        """Test disable loop when already disabled."""
        # Start with loop disabled
        transport = mock_state.get_transport.return_value
        transport.loop_enabled = False

        result = await navigation_tools.disable_loop()

        # Should not toggle
        mock_osc_bridge.send_command.assert_not_called()
        assert result["success"] is True
        assert result["loop_enabled"] is False

    @pytest.mark.asyncio
    async def test_disable_loop_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test disable loop when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.disable_loop()

        assert result["success"] is False
        assert "Not connected" in result["error"]


class TestClearLoopRange:
    """Test clearing loop range."""

    @pytest.mark.asyncio
    async def test_clear_loop_range_success(
        self, navigation_tools, mock_osc_bridge, mock_state
    ):
        """Test successfully clearing loop range."""
        # Start with loop enabled
        transport = mock_state.get_transport.return_value
        transport.loop_enabled = True

        result = await navigation_tools.clear_loop_range()

        mock_osc_bridge.send_command.assert_called_once_with("/loop_toggle")
        assert result["success"] is True
        assert "cleared" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_clear_loop_range_not_connected(
        self, navigation_tools, mock_osc_bridge
    ):
        """Test clear loop range when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.clear_loop_range()

        assert result["success"] is False
        assert "Not connected" in result["error"]


# ==================== Tempo & Time Signature Tests ====================


class TestSetTempo:
    """Test tempo setting."""

    @pytest.mark.asyncio
    async def test_set_tempo_success(self, navigation_tools, mock_osc_bridge):
        """Test successfully setting tempo."""
        result = await navigation_tools.set_tempo(140.0)

        mock_osc_bridge.send_command.assert_called_once_with("/set_tempo", 140.0)
        assert result["success"] is True
        assert result["tempo"] == 140.0

    @pytest.mark.asyncio
    async def test_set_tempo_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test set tempo when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.set_tempo(140.0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_tempo_too_low(self, navigation_tools):
        """Test set tempo with value too low."""
        result = await navigation_tools.set_tempo(10.0)

        assert result["success"] is False
        assert "out of range" in result["error"]

    @pytest.mark.asyncio
    async def test_set_tempo_too_high(self, navigation_tools):
        """Test set tempo with value too high."""
        result = await navigation_tools.set_tempo(400.0)

        assert result["success"] is False
        assert "out of range" in result["error"]

    @pytest.mark.asyncio
    async def test_set_tempo_edge_cases(self, navigation_tools, mock_osc_bridge):
        """Test set tempo at edge values."""
        # Test minimum
        result = await navigation_tools.set_tempo(20.0)
        assert result["success"] is True

        # Test maximum
        result = await navigation_tools.set_tempo(300.0)
        assert result["success"] is True


class TestGetTempo:
    """Test tempo querying."""

    @pytest.mark.asyncio
    async def test_get_tempo_success(self, navigation_tools, mock_state):
        """Test successfully getting tempo."""
        result = await navigation_tools.get_tempo()

        assert result["success"] is True
        assert result["tempo"] == 120.0
        assert "message" in result


class TestSetTimeSignature:
    """Test time signature setting."""

    @pytest.mark.asyncio
    async def test_set_time_signature_success(self, navigation_tools, mock_osc_bridge):
        """Test successfully setting time signature."""
        result = await navigation_tools.set_time_signature(3, 4)

        mock_osc_bridge.send_command.assert_called_once_with(
            "/set_time_signature", 3, 4
        )
        assert result["success"] is True
        assert result["time_signature"] == "3/4"

    @pytest.mark.asyncio
    async def test_set_time_signature_not_connected(
        self, navigation_tools, mock_osc_bridge
    ):
        """Test set time signature when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.set_time_signature(3, 4)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_set_time_signature_invalid_numerator(self, navigation_tools):
        """Test set time signature with invalid numerator."""
        result = await navigation_tools.set_time_signature(0, 4)

        assert result["success"] is False
        assert "out of range" in result["error"]

        result = await navigation_tools.set_time_signature(50, 4)

        assert result["success"] is False
        assert "out of range" in result["error"]

    @pytest.mark.asyncio
    async def test_set_time_signature_invalid_denominator(self, navigation_tools):
        """Test set time signature with invalid denominator."""
        result = await navigation_tools.set_time_signature(4, 3)

        assert result["success"] is False
        assert "must be one of" in result["error"]

    @pytest.mark.asyncio
    async def test_set_time_signature_common_values(
        self, navigation_tools, mock_osc_bridge
    ):
        """Test common time signatures."""
        test_cases = [(4, 4), (3, 4), (6, 8), (2, 4), (5, 4), (7, 8)]

        for numerator, denominator in test_cases:
            result = await navigation_tools.set_time_signature(numerator, denominator)
            assert result["success"] is True


class TestGetTimeSignature:
    """Test time signature querying."""

    @pytest.mark.asyncio
    async def test_get_time_signature_success(self, navigation_tools):
        """Test successfully getting time signature."""
        result = await navigation_tools.get_time_signature()

        assert result["success"] is True
        assert result["time_signature"] == "4/4"
        assert result["numerator"] == 4
        assert result["denominator"] == 4


# ==================== Navigation Helpers Tests ====================


class TestGotoTime:
    """Test jumping to timecode."""

    @pytest.mark.asyncio
    async def test_goto_time_success(self, navigation_tools, mock_osc_bridge):
        """Test successfully jumping to timecode."""
        result = await navigation_tools.goto_time(0, 1, 30, 0)

        # 1 minute 30 seconds = 90 seconds * 48000 = 4320000 frames
        mock_osc_bridge.send_command.assert_called_once_with("/locate", 4320000, 1)
        assert result["success"] is True
        assert result["timecode"] == "00:01:30:00"
        assert result["frame"] == 4320000

    @pytest.mark.asyncio
    async def test_goto_time_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test goto time when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.goto_time(0, 1, 30, 0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_goto_time_negative_values(self, navigation_tools):
        """Test goto time with negative values."""
        result = await navigation_tools.goto_time(-1, 0, 0, 0)

        assert result["success"] is False
        assert "non-negative" in result["error"]

    @pytest.mark.asyncio
    async def test_goto_time_invalid_minutes(self, navigation_tools):
        """Test goto time with invalid minutes."""
        result = await navigation_tools.goto_time(0, 60, 0, 0)

        assert result["success"] is False
        assert "0-59" in result["error"]

    @pytest.mark.asyncio
    async def test_goto_time_invalid_seconds(self, navigation_tools):
        """Test goto time with invalid seconds."""
        result = await navigation_tools.goto_time(0, 0, 60, 0)

        assert result["success"] is False
        assert "0-59" in result["error"]


class TestGotoBar:
    """Test jumping to bar number."""

    @pytest.mark.asyncio
    async def test_goto_bar_success(self, navigation_tools, mock_osc_bridge):
        """Test successfully jumping to bar."""
        result = await navigation_tools.goto_bar(5)

        # Bar 5 at 120 BPM, 4/4 time:
        # 4 bars * 4 beats/bar * 0.5 sec/beat * 48000 samples/sec = 384000 frames
        mock_osc_bridge.send_command.assert_called_with("/locate", 384000, 1)
        assert result["success"] is True
        assert result["bar"] == 5
        assert result["frame"] == 384000

    @pytest.mark.asyncio
    async def test_goto_bar_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test goto bar when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.goto_bar(5)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_goto_bar_invalid(self, navigation_tools):
        """Test goto bar with invalid bar number."""
        result = await navigation_tools.goto_bar(0)

        assert result["success"] is False
        assert "positive" in result["error"]

    @pytest.mark.asyncio
    async def test_goto_bar_first_bar(self, navigation_tools, mock_osc_bridge):
        """Test jumping to first bar."""
        result = await navigation_tools.goto_bar(1)

        # Bar 1 should be frame 0
        mock_osc_bridge.send_command.assert_called_once_with("/locate", 0, 1)
        assert result["success"] is True


class TestSkipForward:
    """Test skipping forward."""

    @pytest.mark.asyncio
    async def test_skip_forward_success(
        self, navigation_tools, mock_osc_bridge, mock_state
    ):
        """Test successfully skipping forward."""
        # Current frame is 48000
        transport = mock_state.get_transport.return_value
        transport.frame = 48000

        result = await navigation_tools.skip_forward(10.0)

        # 10 seconds * 48000 samples/sec = 480000 frames
        # 48000 + 480000 = 528000
        mock_osc_bridge.send_command.assert_called_once_with("/locate", 528000, 1)
        assert result["success"] is True
        assert result["seconds"] == 10.0
        assert result["frame"] == 528000

    @pytest.mark.asyncio
    async def test_skip_forward_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test skip forward when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.skip_forward(10.0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_skip_forward_negative(self, navigation_tools):
        """Test skip forward with negative value."""
        result = await navigation_tools.skip_forward(-5.0)

        assert result["success"] is False
        assert "non-negative" in result["error"]


class TestSkipBackward:
    """Test skipping backward."""

    @pytest.mark.asyncio
    async def test_skip_backward_success(
        self, navigation_tools, mock_osc_bridge, mock_state
    ):
        """Test successfully skipping backward."""
        # Current frame is 48000
        transport = mock_state.get_transport.return_value
        transport.frame = 480000

        result = await navigation_tools.skip_backward(5.0)

        # 5 seconds * 48000 samples/sec = 240000 frames
        # 480000 - 240000 = 240000
        mock_osc_bridge.send_command.assert_called_once_with("/locate", 240000, 1)
        assert result["success"] is True
        assert result["seconds"] == 5.0
        assert result["frame"] == 240000

    @pytest.mark.asyncio
    async def test_skip_backward_to_zero(
        self, navigation_tools, mock_osc_bridge, mock_state
    ):
        """Test skipping backward past frame 0."""
        # Current frame is 48000
        transport = mock_state.get_transport.return_value
        transport.frame = 48000

        result = await navigation_tools.skip_backward(10.0)

        # Should not go below 0
        mock_osc_bridge.send_command.assert_called_once_with("/locate", 0, 1)
        assert result["success"] is True
        assert result["frame"] == 0

    @pytest.mark.asyncio
    async def test_skip_backward_not_connected(self, navigation_tools, mock_osc_bridge):
        """Test skip backward when not connected."""
        mock_osc_bridge.is_connected.return_value = False

        result = await navigation_tools.skip_backward(5.0)

        assert result["success"] is False
        assert "Not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_skip_backward_negative(self, navigation_tools):
        """Test skip backward with negative value."""
        result = await navigation_tools.skip_backward(-5.0)

        assert result["success"] is False
        assert "non-negative" in result["error"]


# ==================== Helper Function Tests ====================


class TestTimecodeToFrames:
    """Test timecode conversion helper."""

    def test_timecode_to_frames_basic(self, navigation_tools):
        """Test basic timecode to frames conversion."""
        # 1 minute = 60 seconds * 48000 samples/sec = 2880000 frames
        frames = navigation_tools._timecode_to_frames(0, 1, 0, 0)
        assert frames == 2880000

    def test_timecode_to_frames_complex(self, navigation_tools):
        """Test complex timecode conversion."""
        # 1 hour, 30 minutes, 45 seconds = 5445 seconds * 48000 = 261360000 frames
        frames = navigation_tools._timecode_to_frames(1, 30, 45, 0)
        assert frames == 261360000

    def test_timecode_to_frames_with_frames(self, navigation_tools):
        """Test timecode conversion with frame component."""
        frames = navigation_tools._timecode_to_frames(0, 0, 1, 100)
        assert frames == 48100  # 1 second * 48000 + 100 frames


class TestBarToFrames:
    """Test bar number conversion helper."""

    def test_bar_to_frames_first_bar(self, navigation_tools):
        """Test conversion of first bar."""
        frames = navigation_tools._bar_to_frames(1)
        assert frames == 0  # First bar starts at 0

    def test_bar_to_frames_second_bar(self, navigation_tools):
        """Test conversion of second bar."""
        # At 120 BPM, 4/4 time: 2 seconds per bar = 96000 frames
        frames = navigation_tools._bar_to_frames(2)
        assert frames == 96000

    def test_bar_to_frames_multiple_bars(self, navigation_tools):
        """Test conversion of multiple bars."""
        # Bar 5 = 4 bars * 2 seconds/bar * 48000 samples/sec = 384000 frames
        frames = navigation_tools._bar_to_frames(5)
        assert frames == 384000
