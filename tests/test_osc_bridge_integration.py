"""
Integration tests for OSC bridge with state management.

Tests the complete workflow of OSC commands and feedback.
"""

from unittest.mock import Mock, AsyncMock, patch
import pytest

from ardour_mcp.ardour_state import ArdourState
from ardour_mcp.osc_bridge import ArdourOSCBridge


class TestOSCBridgeStateSync:
    """Test OSC bridge and state synchronization."""

    def test_feedback_handler_callback_flow(self):
        """Test complete feedback handler callback flow."""
        state = ArdourState()
        callbacks = {}

        def register_handler(address, callback):
            callbacks[address] = callback

        mock_bridge = Mock()
        mock_bridge.register_feedback_handler.side_effect = register_handler

        # Register handlers
        state.register_feedback_handlers(mock_bridge)

        # Verify handlers were registered
        assert "/transport_frame" in callbacks
        assert "/transport_speed" in callbacks
        assert "/tempo" in callbacks

        # Simulate OSC feedback
        callbacks["/transport_frame"]("/transport_frame", [48000])
        assert state.get_transport().frame == 48000

        callbacks["/transport_speed"]("/transport_speed", [1.0])
        assert state.get_transport().playing is True

        callbacks["/tempo"]("/tempo", [140.0])
        assert state.get_transport().tempo == 140.0

    def test_track_feedback_integration(self):
        """Test track feedback handler integration."""
        state = ArdourState()
        callbacks = {}

        def register_handler(address, callback):
            callbacks[address] = callback

        mock_bridge = Mock()
        mock_bridge.register_feedback_handler.side_effect = register_handler

        state.register_feedback_handlers(mock_bridge)

        # Simulate track creation and updates
        callbacks["/strip/name"]("/strip/name", [1, "NewTrack"])
        callbacks["/strip/gain"]("/strip/gain", [1, -6.0])
        callbacks["/strip/pan_stereo_position"]("/strip/pan_stereo_position", [1, -0.3])

        track = state.get_track(1)
        assert track.name == "NewTrack"
        assert track.gain_db == -6.0
        assert track.pan == -0.3

    def test_multiple_track_simultaneous_feedback(self):
        """Test multiple tracks receiving feedback simultaneously."""
        state = ArdourState()
        callbacks = {}

        def register_handler(address, callback):
            callbacks[address] = callback

        mock_bridge = Mock()
        mock_bridge.register_feedback_handler.side_effect = register_handler

        state.register_feedback_handlers(mock_bridge)

        # Create multiple tracks with feedback
        for i in range(1, 5):
            callbacks["/strip/name"]("/strip/name", [i, f"Track{i}"])
            callbacks["/strip/gain"]("/strip/gain", [i, -i])

        tracks = state.get_all_tracks()
        assert len(tracks) == 4
        for i in range(1, 5):
            assert tracks[i].name == f"Track{i}"
            assert tracks[i].gain_db == -i


class TestStateExceptionHandling:
    """Test exception handling in state management."""

    def test_handler_with_empty_args(self):
        """Test handlers with empty argument list."""
        state = ArdourState()

        # Empty args should be handled gracefully
        state._on_transport_frame("/transport_frame", [])
        state._on_tempo("/tempo", [])
        # Should not update state

        assert state.get_transport().frame == 0
        assert state.get_transport().tempo == 120.0

    def test_handler_with_insufficient_args(self):
        """Test handlers with insufficient arguments."""
        state = ArdourState()

        # Single arg where two expected
        state._on_strip_gain("/strip/gain", [1])
        # Should not crash, just not update

        # Two args for single arg field
        state._on_tempo("/tempo", [140.0, 150.0])
        # Should update with first value
        assert state.get_transport().tempo == 140.0

    def test_handler_with_type_coercion(self):
        """Test handlers with type coercion."""
        state = ArdourState()

        # Int that needs to be converted
        state._on_tempo("/tempo", [int(140)])
        assert state.get_transport().tempo == 140

        # Test that it still processes valid values
        state._on_transport_frame("/transport_frame", [1000])
        assert state.get_transport().frame == 1000


class TestConcurrentStateUpdates:
    """Test concurrent state updates."""

    def test_rapid_transport_updates(self):
        """Test rapid transport state updates."""
        state = ArdourState()

        # Simulate rapid feedback
        for frame in range(0, 10000, 100):
            state._on_transport_frame("/transport_frame", [frame])
            state._on_transport_speed("/transport_speed", [1.0])

        # Final state should be consistent
        assert state.get_transport().frame == 9900
        assert state.get_transport().playing is True

    def test_rapid_track_updates(self):
        """Test rapid track state updates."""
        state = ArdourState()

        # Simulate rapid track updates
        for i in range(1, 100):
            state._on_strip_gain("/strip/gain", [1, float(i) / 10.0])

        assert state.get_track(1).gain_db == 9.9


class TestStateConsistency:
    """Test state remains consistent under various operations."""

    def test_state_after_multiple_clear_operations(self):
        """Test state remains consistent after multiple clears."""
        state = ArdourState()

        for _ in range(5):
            state.update_track(1, name="Track1")
            assert state.get_track(1) is not None

            state.clear()
            assert state.get_track(1) is None

    def test_track_isolation(self):
        """Test that track updates don't affect other tracks."""
        state = ArdourState()

        state.update_track(1, name="Track1", gain_db=-6.0)
        state.update_track(2, name="Track2", gain_db=-3.0)

        # Update track 1
        state.update_track(1, pan=0.5)

        # Verify track 2 is unaffected
        assert state.get_track(2).pan == 0.0
        assert state.get_track(2).gain_db == -3.0


class TestFeedbackHandlerOrdering:
    """Test that handler ordering doesn't affect consistency."""

    def test_handlers_order_invariance(self):
        """Test that handler call order doesn't matter."""
        state1 = ArdourState()
        state2 = ArdourState()

        # Apply feedback in different order
        state1._on_strip_name("/strip/name", [1, "Track"])
        state1._on_strip_gain("/strip/gain", [1, -6.0])
        state1._on_strip_mute("/strip/mute", [1, 1])

        state2._on_strip_mute("/strip/mute", [1, 1])
        state2._on_strip_gain("/strip/gain", [1, -6.0])
        state2._on_strip_name("/strip/name", [1, "Track"])

        # Final states should be identical
        track1 = state1.get_track(1)
        track2 = state2.get_track(1)

        assert track1.name == track2.name
        assert track1.gain_db == track2.gain_db
        assert track1.muted == track2.muted


class TestComplexFeedbackSequences:
    """Test complex feedback sequences."""

    def test_session_initialization_sequence(self):
        """Test complete session initialization sequence."""
        state = ArdourState()

        # Session starts
        state._on_session_name("/session_name", ["NewSession"])
        state._on_sample_rate("/sample_rate", [48000])
        state._on_tempo("/tempo", [120.0])
        state._on_time_signature("/time_signature", [4, 4])

        # Load tracks
        for i in range(1, 4):
            state._on_strip_name("/strip/name", [i, f"Track{i}"])
            state._on_strip_gain("/strip/gain", [i, 0.0])

        # Verify complete state
        session = state.get_session_info()
        assert session.name == "NewSession"
        assert session.sample_rate == 48000
        assert session.transport.tempo == 120.0
        assert len(session.tracks) == 3

    def test_playback_start_stop_sequence(self):
        """Test playback start/stop sequence."""
        state = ArdourState()

        # Prepare
        state._on_transport_frame("/transport_frame", [0])
        state._on_transport_speed("/transport_speed", [0.0])

        # Play
        state._on_transport_speed("/transport_speed", [1.0])
        assert state.get_transport().playing is True

        # Simulate playback
        for frame in [1000, 2000, 3000]:
            state._on_transport_frame("/transport_frame", [frame])

        # Stop
        state._on_transport_speed("/transport_speed", [0.0])
        assert state.get_transport().playing is False
        assert state.get_transport().frame == 3000

    def test_recording_workflow_sequence(self):
        """Test complete recording workflow."""
        state = ArdourState()

        # Create recording track
        state._on_strip_name("/strip/name", [1, "Recording"])
        state._on_strip_recenable("/strip/recenable", [1, 0])

        # Arm for recording
        state._on_strip_recenable("/strip/recenable", [1, 1])
        assert state.get_track(1).rec_enabled is True

        # Start recording
        state._on_record_enabled("/record_enabled", [1])
        state._on_transport_speed("/transport_speed", [1.0])
        assert state.get_transport().recording is True
        assert state.get_transport().playing is True

        # Record for a while
        for frame in [0, 48000, 96000, 144000]:
            state._on_transport_frame("/transport_frame", [frame])

        # Stop recording
        state._on_transport_speed("/transport_speed", [0.0])
        state._on_record_enabled("/record_enabled", [0])
        assert state.get_transport().recording is False


class TestStateRecovery:
    """Test state recovery from edge cases."""

    def test_recovery_from_missing_track_fields(self):
        """Test recovery when track feedback is incomplete."""
        state = ArdourState()

        # Create track with minimal feedback
        state._on_strip_name("/strip/name", [1, "Track"])

        # Add more properties
        state._on_strip_gain("/strip/gain", [1, -3.0])

        track = state.get_track(1)
        assert track.name == "Track"
        assert track.gain_db == -3.0

    def test_recovery_from_out_of_order_feedback(self):
        """Test recovery from out-of-order feedback."""
        state = ArdourState()

        # Feedback arrives out of order
        state._on_strip_gain("/strip/gain", [1, -6.0])  # Before name
        state._on_strip_name("/strip/name", [1, "Track"])

        track = state.get_track(1)
        assert track.name == "Track"
        assert track.gain_db == -6.0
