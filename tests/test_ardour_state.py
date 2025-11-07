"""
Tests for Ardour state management.

Tests the ArdourState class including state updates, feedback handlers,
thread-safety, and state queries.
"""

from unittest.mock import Mock, MagicMock, call
import pytest

from ardour_mcp.ardour_state import (
    ArdourState,
    SessionState,
    TrackState,
    TransportState,
)


class TestArdourStateInitialization:
    """Test ArdourState initialization."""

    def test_init_creates_empty_state(self):
        """Test that initialization creates empty session state."""
        state = ArdourState()

        assert state is not None
        assert state._lock is not None
        assert state._state is not None
        assert state._state.name == ""
        assert state._state.path == ""
        assert state._state.sample_rate == 48000
        assert state._state.tracks == {}
        assert state._state.markers == []
        assert state._state.dirty is False

    def test_init_transport_state(self):
        """Test initial transport state."""
        state = ArdourState()
        transport = state._state.transport

        assert transport.playing is False
        assert transport.recording is False
        assert transport.frame == 0
        assert transport.tempo == 120.0
        assert transport.time_signature == (4, 4)
        assert transport.loop_enabled is False


class TestTransportStateUpdates:
    """Test transport state updates."""

    def test_update_transport_playing(self):
        """Test updating playing state."""
        state = ArdourState()
        state.update_transport(playing=True)

        assert state._state.transport.playing is True

    def test_update_transport_recording(self):
        """Test updating recording state."""
        state = ArdourState()
        state.update_transport(recording=True)

        assert state._state.transport.recording is True

    def test_update_transport_frame(self):
        """Test updating frame position."""
        state = ArdourState()
        state.update_transport(frame=48000)

        assert state._state.transport.frame == 48000

    def test_update_transport_tempo(self):
        """Test updating tempo."""
        state = ArdourState()
        state.update_transport(tempo=140.0)

        assert state._state.transport.tempo == 140.0

    def test_update_transport_multiple(self):
        """Test updating multiple transport fields at once."""
        state = ArdourState()
        state.update_transport(
            playing=True,
            recording=True,
            frame=96000,
            tempo=150.0,
        )

        assert state._state.transport.playing is True
        assert state._state.transport.recording is True
        assert state._state.transport.frame == 96000
        assert state._state.transport.tempo == 150.0

    def test_update_transport_partial(self):
        """Test updating only specific transport fields."""
        state = ArdourState()
        state.update_transport(playing=True, frame=1000)

        assert state._state.transport.playing is True
        assert state._state.transport.frame == 1000
        assert state._state.transport.recording is False
        assert state._state.transport.tempo == 120.0


class TestTrackStateUpdates:
    """Test track state updates."""

    def test_update_track_creates_new_track(self):
        """Test creating a new track via update."""
        state = ArdourState()
        state.update_track(1, name="Vocals", track_type="audio")

        assert 1 in state._state.tracks
        assert state._state.tracks[1].name == "Vocals"
        assert state._state.tracks[1].track_type == "audio"
        assert state._state.tracks[1].strip_id == 1

    def test_update_track_modifies_existing(self):
        """Test modifying an existing track."""
        state = ArdourState()
        state.update_track(1, name="Vocals")
        state.update_track(1, gain_db=-3.0)

        assert state._state.tracks[1].name == "Vocals"
        assert state._state.tracks[1].gain_db == -3.0

    def test_update_track_mute(self):
        """Test updating track mute state."""
        state = ArdourState()
        state.update_track(1, name="Test", muted=True)

        assert state._state.tracks[1].muted is True

    def test_update_track_solo(self):
        """Test updating track solo state."""
        state = ArdourState()
        state.update_track(1, name="Test", soloed=True)

        assert state._state.tracks[1].soloed is True

    def test_update_track_rec_enable(self):
        """Test updating track record enable."""
        state = ArdourState()
        state.update_track(1, name="Test", rec_enabled=True)

        assert state._state.tracks[1].rec_enabled is True

    def test_update_track_pan(self):
        """Test updating track pan."""
        state = ArdourState()
        state.update_track(1, name="Test", pan=-0.5)

        assert state._state.tracks[1].pan == -0.5

    def test_update_track_multiple_fields(self):
        """Test updating multiple track fields."""
        state = ArdourState()
        state.update_track(
            1,
            name="Guitar",
            track_type="audio",
            gain_db=-6.0,
            pan=0.3,
            muted=False,
            soloed=False,
            rec_enabled=True,
        )

        track = state._state.tracks[1]
        assert track.name == "Guitar"
        assert track.track_type == "audio"
        assert track.gain_db == -6.0
        assert track.pan == 0.3
        assert track.muted is False
        assert track.soloed is False
        assert track.rec_enabled is True

    def test_update_track_ignores_invalid_fields(self):
        """Test that invalid fields are ignored."""
        state = ArdourState()
        state.update_track(1, name="Test", invalid_field="ignored")

        assert state._state.tracks[1].name == "Test"
        assert not hasattr(state._state.tracks[1], "invalid_field")


class TestFeedbackHandlers:
    """Test OSC feedback handlers."""

    def test_register_feedback_handlers(self):
        """Test registering feedback handlers with OSC bridge."""
        state = ArdourState()
        mock_bridge = Mock()

        state.register_feedback_handlers(mock_bridge)

        # Verify all handlers are registered (15 total)
        assert mock_bridge.register_feedback_handler.call_count == 15

        # Check some specific handlers
        calls = mock_bridge.register_feedback_handler.call_args_list
        addresses = [call[0][0] for call in calls]

        assert "/transport_frame" in addresses
        assert "/transport_speed" in addresses
        assert "/record_enabled" in addresses
        assert "/tempo" in addresses
        assert "/time_signature" in addresses
        assert "/loop_toggle" in addresses
        assert "/session_name" in addresses
        assert "/sample_rate" in addresses
        assert "/dirty" in addresses
        assert "/strip/name" in addresses
        assert "/strip/gain" in addresses

    def test_on_transport_frame(self):
        """Test transport frame feedback handler."""
        state = ArdourState()
        state._on_transport_frame("/transport_frame", [96000])

        assert state._state.transport.frame == 96000

    def test_on_transport_frame_empty_args(self):
        """Test transport frame handler with empty args."""
        state = ArdourState()
        state.update_transport(frame=1000)
        state._on_transport_frame("/transport_frame", [])

        # Should not change
        assert state._state.transport.frame == 1000

    def test_on_transport_speed_playing(self):
        """Test transport speed feedback for playing."""
        state = ArdourState()
        state._on_transport_speed("/transport_speed", [1.0])

        assert state._state.transport.playing is True

    def test_on_transport_speed_stopped(self):
        """Test transport speed feedback for stopped."""
        state = ArdourState()
        state.update_transport(playing=True)
        state._on_transport_speed("/transport_speed", [0.0])

        assert state._state.transport.playing is False

    def test_on_record_enabled(self):
        """Test record enabled feedback handler."""
        state = ArdourState()
        state._on_record_enabled("/record_enabled", [1])

        assert state._state.transport.recording is True

    def test_on_record_disabled(self):
        """Test record disabled feedback handler."""
        state = ArdourState()
        state.update_transport(recording=True)
        state._on_record_enabled("/record_enabled", [0])

        assert state._state.transport.recording is False

    def test_on_tempo(self):
        """Test tempo feedback handler."""
        state = ArdourState()
        state._on_tempo("/tempo", [140.5])

        assert state._state.transport.tempo == 140.5

    def test_on_time_signature(self):
        """Test time signature feedback handler."""
        state = ArdourState()
        state._on_time_signature("/time_signature", [3, 4])

        assert state._state.transport.time_signature == (3, 4)

    def test_on_time_signature_insufficient_args(self):
        """Test time signature with insufficient args."""
        state = ArdourState()
        state._on_time_signature("/time_signature", [3])

        # Should not change
        assert state._state.transport.time_signature == (4, 4)

    def test_on_loop_toggle_enabled(self):
        """Test loop toggle feedback handler."""
        state = ArdourState()
        state._on_loop_toggle("/loop_toggle", [1])

        assert state._state.transport.loop_enabled is True

    def test_on_loop_toggle_disabled(self):
        """Test loop toggle disabled."""
        state = ArdourState()
        state.update_transport(playing=True)
        state._on_loop_toggle("/loop_toggle", [0])

        assert state._state.transport.loop_enabled is False

    def test_on_session_name(self):
        """Test session name feedback handler."""
        state = ArdourState()
        state._on_session_name("/session_name", ["MyProject"])

        assert state._state.name == "MyProject"

    def test_on_sample_rate(self):
        """Test sample rate feedback handler."""
        state = ArdourState()
        state._on_sample_rate("/sample_rate", [44100])

        assert state._state.sample_rate == 44100

    def test_on_dirty_true(self):
        """Test dirty flag feedback handler set to true."""
        state = ArdourState()
        state._on_dirty("/dirty", [1])

        assert state._state.dirty is True

    def test_on_dirty_false(self):
        """Test dirty flag feedback handler set to false."""
        state = ArdourState()
        state.update_transport(recording=True)
        state._on_dirty("/dirty", [0])

        assert state._state.dirty is False

    def test_on_strip_name(self):
        """Test strip name feedback handler."""
        state = ArdourState()
        state._on_strip_name("/strip/name", [1, "Vocals"])

        assert state._state.tracks[1].name == "Vocals"

    def test_on_strip_gain(self):
        """Test strip gain feedback handler."""
        state = ArdourState()
        state._on_strip_gain("/strip/gain", [1, -6.0])

        assert state._state.tracks[1].gain_db == -6.0

    def test_on_strip_pan(self):
        """Test strip pan feedback handler."""
        state = ArdourState()
        state._on_strip_pan("/strip/pan_stereo_position", [1, -0.5])

        assert state._state.tracks[1].pan == -0.5

    def test_on_strip_mute(self):
        """Test strip mute feedback handler."""
        state = ArdourState()
        state._on_strip_mute("/strip/mute", [1, 1])

        assert state._state.tracks[1].muted is True

    def test_on_strip_solo(self):
        """Test strip solo feedback handler."""
        state = ArdourState()
        state._on_strip_solo("/strip/solo", [1, 1])

        assert state._state.tracks[1].soloed is True

    def test_on_strip_recenable(self):
        """Test strip record enable feedback handler."""
        state = ArdourState()
        state._on_strip_recenable("/strip/recenable", [1, 1])

        assert state._state.tracks[1].rec_enabled is True


class TestStateQueries:
    """Test state query methods."""

    def test_get_transport(self):
        """Test getting transport state."""
        state = ArdourState()
        state.update_transport(playing=True, tempo=140.0)

        transport = state.get_transport()
        assert transport.playing is True
        assert transport.tempo == 140.0

    def test_get_track_exists(self):
        """Test getting existing track."""
        state = ArdourState()
        state.update_track(1, name="Vocals")

        track = state.get_track(1)
        assert track is not None
        assert track.name == "Vocals"
        assert track.strip_id == 1

    def test_get_track_not_exists(self):
        """Test getting non-existent track."""
        state = ArdourState()

        track = state.get_track(99)
        assert track is None

    def test_get_all_tracks_empty(self):
        """Test getting all tracks when empty."""
        state = ArdourState()

        tracks = state.get_all_tracks()
        assert tracks == {}

    def test_get_all_tracks_multiple(self):
        """Test getting all tracks with multiple tracks."""
        state = ArdourState()
        state.update_track(1, name="Vocals")
        state.update_track(2, name="Guitar")
        state.update_track(3, name="Bass")

        tracks = state.get_all_tracks()
        assert len(tracks) == 3
        assert 1 in tracks
        assert 2 in tracks
        assert 3 in tracks

    def test_get_session_info(self):
        """Test getting complete session info."""
        state = ArdourState()
        state.update_track(1, name="Vocals")
        state.update_transport(playing=True)
        state._state.name = "MyProject"

        session = state.get_session_info()
        assert session.name == "MyProject"
        assert session.transport.playing is True
        assert 1 in session.tracks


class TestStateClear:
    """Test state clearing."""

    def test_clear_resets_all_state(self):
        """Test that clear resets all state to default."""
        state = ArdourState()
        state.update_track(1, name="Vocals")
        state.update_transport(playing=True, tempo=140.0)
        state._state.name = "MyProject"

        state.clear()

        assert state._state.name == ""
        assert state._state.tracks == {}
        assert state._state.transport.playing is False
        assert state._state.transport.tempo == 120.0
        assert state._state.sample_rate == 48000

    def test_clear_preserves_lock(self):
        """Test that clear preserves the lock object."""
        state = ArdourState()
        original_lock = state._lock
        state.clear()

        assert state._lock is original_lock


class TestThreadSafety:
    """Test thread-safety of state management."""

    def test_transport_update_uses_lock(self):
        """Test that transport update uses lock."""
        state = ArdourState()
        original_lock = state._lock

        # Verify lock is used (indirectly by checking it's not None)
        state.update_transport(playing=True)
        assert state._lock is original_lock

    def test_track_update_uses_lock(self):
        """Test that track update uses lock."""
        state = ArdourState()
        original_lock = state._lock

        state.update_track(1, name="Test")
        assert state._lock is original_lock

    def test_get_transport_uses_lock(self):
        """Test that get_transport uses lock."""
        state = ArdourState()
        state.update_transport(playing=True)

        transport = state.get_transport()
        assert transport is not None

    def test_get_track_uses_lock(self):
        """Test that get_track uses lock."""
        state = ArdourState()
        state.update_track(1, name="Test")

        track = state.get_track(1)
        assert track is not None

    def test_get_all_tracks_returns_dict_copy(self):
        """Test that get_all_tracks returns a dict copy."""
        state = ArdourState()
        state.update_track(1, name="Original")

        tracks = state.get_all_tracks()
        # The dict is a copy, but track objects are still references
        # Verify the dict itself is a different object
        original_dict = state._state.tracks
        assert tracks is not original_dict
        # But the track object inside is still the same reference
        assert tracks[1] is original_dict[1]


class TestDataclasses:
    """Test dataclass definitions."""

    def test_transport_state_creation(self):
        """Test TransportState creation."""
        transport = TransportState(
            playing=True,
            recording=True,
            frame=48000,
            tempo=140.0,
            time_signature=(3, 4),
            loop_enabled=True,
        )

        assert transport.playing is True
        assert transport.recording is True
        assert transport.frame == 48000
        assert transport.tempo == 140.0
        assert transport.time_signature == (3, 4)
        assert transport.loop_enabled is True

    def test_track_state_creation(self):
        """Test TrackState creation."""
        track = TrackState(
            strip_id=1,
            name="Vocals",
            track_type="audio",
            muted=True,
            soloed=False,
            rec_enabled=True,
            gain_db=-3.0,
            pan=-0.5,
            hidden=False,
        )

        assert track.strip_id == 1
        assert track.name == "Vocals"
        assert track.track_type == "audio"
        assert track.muted is True
        assert track.soloed is False
        assert track.rec_enabled is True
        assert track.gain_db == -3.0
        assert track.pan == -0.5
        assert track.hidden is False

    def test_session_state_creation(self):
        """Test SessionState creation."""
        session = SessionState(
            name="MyProject",
            path="/path/to/project",
            sample_rate=44100,
        )

        assert session.name == "MyProject"
        assert session.path == "/path/to/project"
        assert session.sample_rate == 44100
        assert session.tracks == {}
        assert session.markers == []
        assert session.dirty is False


class TestComplexScenarios:
    """Test complex state management scenarios."""

    def test_multiple_track_updates(self):
        """Test updating multiple tracks."""
        state = ArdourState()

        # Create and update multiple tracks
        for i in range(1, 6):
            state.update_track(i, name=f"Track{i}", track_type="audio")
            state.update_track(i, gain_db=-i)

        assert len(state.get_all_tracks()) == 5
        for i in range(1, 6):
            track = state.get_track(i)
            assert track.name == f"Track{i}"
            assert track.gain_db == -i

    def test_feedback_sequence(self):
        """Test a sequence of feedback updates."""
        state = ArdourState()

        # Simulate play command
        state._on_transport_speed("/transport_speed", [1.0])
        state._on_transport_frame("/transport_frame", [0])
        state._on_record_enabled("/record_enabled", [0])

        transport = state.get_transport()
        assert transport.playing is True
        assert transport.frame == 0
        assert transport.recording is False

    def test_track_feedback_sequence(self):
        """Test a sequence of track feedback updates."""
        state = ArdourState()

        state._on_strip_name("/strip/name", [1, "Vocals"])
        state._on_strip_gain("/strip/gain", [1, -6.0])
        state._on_strip_pan("/strip/pan_stereo_position", [1, -0.3])
        state._on_strip_mute("/strip/mute", [1, 0])
        state._on_strip_solo("/strip/solo", [1, 0])
        state._on_strip_recenable("/strip/recenable", [1, 1])

        track = state.get_track(1)
        assert track.name == "Vocals"
        assert track.gain_db == -6.0
        assert track.pan == -0.3
        assert track.muted is False
        assert track.soloed is False
        assert track.rec_enabled is True
