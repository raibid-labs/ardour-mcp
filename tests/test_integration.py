"""
Integration tests for Ardour MCP components.

Tests the interaction between multiple components including OSC bridge,
state management, and tools.
"""

from unittest.mock import Mock, AsyncMock, patch
import pytest

from ardour_mcp.ardour_state import ArdourState, TrackState, TransportState
from ardour_mcp.osc_bridge import ArdourOSCBridge
from ardour_mcp.server import ArdourMCPServer
from ardour_mcp.tools.mixer import MixerTools
from ardour_mcp.tools.transport import TransportTools
from ardour_mcp.tools.tracks import TrackTools


class TestOSCBridgeStateIntegration:
    """Test integration between OSC bridge and state management."""

    def test_feedback_updates_state(self):
        """Test that feedback handlers update state correctly."""
        state = ArdourState()

        # Simulate OSC feedback
        state._on_transport_speed("/transport_speed", [1.0])
        state._on_transport_frame("/transport_frame", [48000])
        state._on_tempo("/tempo", [140.0])

        transport = state.get_transport()
        assert transport.playing is True
        assert transport.frame == 48000
        assert transport.tempo == 140.0

    def test_multiple_track_feedback_updates(self):
        """Test multiple tracks receiving feedback updates."""
        state = ArdourState()

        # Update multiple tracks
        state._on_strip_name("/strip/name", [1, "Vocals"])
        state._on_strip_gain("/strip/gain", [1, -6.0])
        state._on_strip_mute("/strip/mute", [1, 0])

        state._on_strip_name("/strip/name", [2, "Guitar"])
        state._on_strip_gain("/strip/gain", [2, -3.0])
        state._on_strip_pan("/strip/pan_stereo_position", [2, -0.5])

        tracks = state.get_all_tracks()
        assert len(tracks) == 2
        assert tracks[1].name == "Vocals"
        assert tracks[1].gain_db == -6.0
        assert tracks[2].name == "Guitar"
        assert tracks[2].pan == -0.5

    def test_session_state_updates(self):
        """Test session-level state updates."""
        state = ArdourState()

        state._on_session_name("/session_name", ["MyProject"])
        state._on_sample_rate("/sample_rate", [44100])
        state._on_dirty("/dirty", [1])

        session = state.get_session_info()
        assert session.name == "MyProject"
        assert session.sample_rate == 44100
        assert session.dirty is True


class TestServerStateToolIntegration:
    """Test integration of server, state, and tools."""

    def test_server_tools_access_shared_state(self):
        """Test that all tools can access and modify shared state."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            # Simulate state update
            server.state.update_track(1, name="Vocals", gain_db=-6.0)

            # Verify all tools have access to the same state
            track_from_mixer = server.mixer_tools.state.get_track(1)
            track_from_transport = server.transport_tools.state.get_track(1)

            assert track_from_mixer.name == "Vocals"
            assert track_from_transport.name == "Vocals"
            assert track_from_mixer is track_from_transport

    def test_server_tools_share_osc_bridge(self):
        """Test that all tools use the same OSC bridge."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = Mock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            # Verify all tools use same bridge
            assert server.mixer_tools.osc is mock_bridge
            assert server.transport_tools.osc is mock_bridge
            assert server.track_tools.osc is mock_bridge
            assert server.navigation_tools.osc is mock_bridge
            assert server.session_tools.osc is mock_bridge

    def test_multiple_tools_operating_on_state(self):
        """Test multiple tools operating on the same state."""
        with patch("ardour_mcp.server.ArdourOSCBridge"):
            server = ArdourMCPServer()

            # Simulate initial state from feedback
            server.state.update_track(1, name="Track1", muted=False)
            server.state.update_track(2, name="Track2", soloed=False)
            server.state.update_transport(playing=False, recording=False)

            # Verify tools can access this state
            track1 = server.mixer_tools.state.get_track(1)
            track2 = server.track_tools.state.get_track(2)
            transport = server.transport_tools.state.get_transport()

            assert track1.name == "Track1"
            assert track2.name == "Track2"
            assert transport.playing is False


class TestMultiToolWorkflows:
    """Test workflows involving multiple tools."""

    def test_track_creation_and_mixer_control_workflow(self):
        """Test creating a track and then controlling it with mixer tools."""
        mock_bridge = Mock()
        mock_bridge.is_connected.return_value = True
        state = ArdourState()

        # Simulate track creation response
        state.update_track(1, name="NewTrack", track_type="audio")

        # Verify mixer can control the track
        track = state.get_track(1)
        assert track is not None
        assert track.name == "NewTrack"

        # Update track properties
        state.update_track(1, gain_db=-3.0, pan=0.5)
        track = state.get_track(1)
        assert track.gain_db == -3.0
        assert track.pan == 0.5

    def test_recording_workflow(self):
        """Test complete recording workflow."""
        state = ArdourState()

        # Prepare recording
        state.update_track(1, name="RecordTrack", rec_enabled=False)
        state.update_transport(recording=False, playing=False)

        # Enable recording
        state.update_track(1, rec_enabled=True)
        state.update_transport(recording=True)

        # Verify recording state
        assert state.get_track(1).rec_enabled is True
        assert state.get_transport().recording is True

        # Stop recording
        state.update_transport(recording=False)
        assert state.get_transport().recording is False

    def test_mixing_workflow(self):
        """Test a mixing workflow with multiple tracks."""
        state = ArdourState()

        # Create multiple tracks
        for i in range(1, 4):
            state.update_track(i, name=f"Track{i}", muted=False, soloed=False)

        # Mix the tracks
        state.update_track(1, gain_db=-6.0, pan=-0.3)  # Left channel
        state.update_track(2, gain_db=-3.0, pan=0.0)   # Center
        state.update_track(3, gain_db=-2.0, pan=0.3)   # Right channel

        # Verify mixing state
        tracks = state.get_all_tracks()
        assert tracks[1].gain_db == -6.0
        assert tracks[1].pan == -0.3
        assert tracks[2].gain_db == -3.0
        assert tracks[3].gain_db == -2.0


class TestStateConsistency:
    """Test state consistency across operations."""

    def test_state_consistency_after_multiple_updates(self):
        """Test that state remains consistent after multiple updates."""
        state = ArdourState()

        # Create tracks
        state.update_track(1, name="Vocals")
        state.update_track(2, name="Guitar")

        # Update tracks multiple times
        for i in range(10):
            state.update_track(1, gain_db=-i)
            state.update_track(2, pan=i / 10.0)

        # Verify final state
        track1 = state.get_track(1)
        track2 = state.get_track(2)

        assert track1.gain_db == -9
        assert track2.pan == 0.9

    def test_transport_state_consistency(self):
        """Test transport state consistency."""
        state = ArdourState()

        # Simulate playback sequence
        state.update_transport(playing=False, frame=0)
        state.update_transport(playing=True)  # Start playing
        state.update_transport(frame=1000)
        state.update_transport(frame=2000)
        state.update_transport(frame=3000)
        state.update_transport(playing=False)  # Stop playing

        transport = state.get_transport()
        assert transport.playing is False
        assert transport.frame == 3000

    def test_concurrent_track_updates(self):
        """Test that multiple track updates don't interfere."""
        state = ArdourState()

        # Update multiple tracks in sequence
        state.update_track(1, name="A", gain_db=-1.0, pan=-1.0)
        state.update_track(2, name="B", gain_db=-2.0, pan=-0.5)
        state.update_track(3, name="C", gain_db=-3.0, pan=0.0)
        state.update_track(1, muted=True)  # Update track 1 again
        state.update_track(2, soloed=True)  # Update track 2 again

        # Verify all updates are present
        t1 = state.get_track(1)
        t2 = state.get_track(2)
        t3 = state.get_track(3)

        assert t1.name == "A" and t1.muted is True
        assert t2.name == "B" and t2.soloed is True
        assert t3.name == "C" and t3.pan == 0.0


class TestFeedbackHandlerChaining:
    """Test chains of feedback handlers updating state."""

    def test_transport_feedback_chain(self):
        """Test a chain of transport feedback updates."""
        state = ArdourState()

        # Simulate real feedback sequence
        state._on_transport_speed("/transport_speed", [0.0])  # Stopped
        assert state.get_transport().playing is False

        state._on_transport_frame("/transport_frame", [0])  # At start
        assert state.get_transport().frame == 0

        state._on_transport_speed("/transport_speed", [1.0])  # Playing
        assert state.get_transport().playing is True

        # Simulate playback
        for frame in [1000, 2000, 3000, 4000, 5000]:
            state._on_transport_frame("/transport_frame", [frame])
            assert state.get_transport().frame == frame

        state._on_transport_speed("/transport_speed", [0.0])  # Stop
        assert state.get_transport().playing is False

    def test_track_feedback_chain(self):
        """Test a chain of track feedback updates."""
        state = ArdourState()

        # Create track with feedback
        state._on_strip_name("/strip/name", [1, "NewTrack"])
        state._on_strip_gain("/strip/gain", [1, 0.0])
        state._on_strip_pan("/strip/pan_stereo_position", [1, 0.0])

        track = state.get_track(1)
        assert track.name == "NewTrack"
        assert track.gain_db == 0.0
        assert track.pan == 0.0

        # Modify track
        state._on_strip_gain("/strip/gain", [1, -6.0])
        state._on_strip_mute("/strip/mute", [1, 1])

        track = state.get_track(1)
        assert track.gain_db == -6.0
        assert track.muted is True


class TestServerLifecycleStateIntegration:
    """Test state behavior during server lifecycle."""

    @pytest.mark.asyncio
    async def test_state_cleared_on_stop(self):
        """Test that state is cleared when server stops."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            # Add some state
            server.state.update_track(1, name="Test")
            server.state.update_transport(playing=True)
            server.state._state.name = "TestProject"

            # Verify state is populated
            assert server.state.get_track(1) is not None
            assert server.state.get_transport().playing is True

            # Stop server (clears state)
            await server.stop()

            # Verify state is cleared
            assert server.state.get_track(1) is None
            assert server.state.get_transport().playing is False
            assert server.state._state.name == ""

    @pytest.mark.asyncio
    async def test_feedback_handlers_registered_before_tools(self):
        """Test that feedback handlers are registered before tools run."""
        with patch("ardour_mcp.server.ArdourOSCBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            server = ArdourMCPServer()

            # Patch register_feedback_handlers to track calls
            call_log = []

            original_register = server.state.register_feedback_handlers

            def tracked_register(bridge):
                call_log.append("register_feedback_handlers")
                return original_register(bridge)

            server.state.register_feedback_handlers = tracked_register

            await server.start()

            # Verify handlers were registered
            assert "register_feedback_handlers" in call_log


class TestErrorRecoveryIntegration:
    """Test error handling across integrated components."""

    def test_invalid_feedback_doesnt_break_state(self):
        """Test that invalid feedback doesn't corrupt state."""
        state = ArdourState()

        # Valid feedback
        state._on_strip_name("/strip/name", [1, "Test"])
        assert state.get_track(1).name == "Test"

        # Invalid feedback (empty args)
        state._on_strip_gain("/strip/gain", [])
        # State should remain unchanged
        assert state.get_track(1).name == "Test"

        # Another invalid feedback
        state._on_tempo("/tempo", [])
        # Transport state should remain unchanged
        assert state.get_transport().tempo == 120.0

    def test_malformed_feedback_handling(self):
        """Test handling of malformed feedback."""
        state = ArdourState()

        # Try feedback with missing arguments
        state._on_strip_mute("/strip/mute", [1])  # Missing second arg
        # Should not crash and create empty track

        # Now provide proper feedback
        state._on_strip_mute("/strip/mute", [1, 1])
        assert state.get_track(1).muted is True

    def test_state_recovery_after_operations(self):
        """Test that state remains recoverable after operations."""
        state = ArdourState()

        # Build state
        state.update_track(1, name="T1")
        state.update_track(2, name="T2")
        state.update_transport(playing=True)

        # Clear and rebuild
        state.clear()
        assert state.get_track(1) is None

        state.update_track(1, name="NewT1")
        assert state.get_track(1).name == "NewT1"


class TestComplexMultiModuleScenarios:
    """Test complex scenarios involving multiple modules."""

    def test_full_session_simulation(self):
        """Test a full session simulation with multiple modules."""
        state = ArdourState()

        # Session starts
        state._on_session_name("/session_name", ["MySession"])
        state._on_sample_rate("/sample_rate", [48000])

        # Create tracks
        for i in range(1, 4):
            state._on_strip_name("/strip/name", [i, f"Track{i}"])
            state._on_strip_gain("/strip/gain", [i, -3.0])
            state._on_strip_mute("/strip/mute", [i, 0])

        # Enable recording on first track
        state._on_strip_recenable("/strip/recenable", [1, 1])

        # Start transport
        state._on_transport_speed("/transport_speed", [1.0])
        state._on_record_enabled("/record_enabled", [1])

        # Simulate playback
        for frame in [0, 48000, 96000, 144000]:
            state._on_transport_frame("/transport_frame", [frame])

        # Stop
        state._on_transport_speed("/transport_speed", [0.0])
        state._on_record_enabled("/record_enabled", [0])

        # Verify final state
        session = state.get_session_info()
        assert session.name == "MySession"
        assert len(session.tracks) == 3
        assert session.transport.recording is False
        assert session.transport.playing is False

    def test_mixer_session_workflow(self):
        """Test a complete mixing session workflow."""
        state = ArdourState()

        # Create band setup
        tracks_config = [
            (1, "Drums", "audio", -6.0, 0.0),
            (2, "Bass", "audio", -3.0, 0.0),
            (3, "Guitar", "audio", -2.0, -0.3),
            (4, "Vocals", "audio", 0.0, 0.3),
        ]

        for strip_id, name, track_type, gain, pan in tracks_config:
            state._on_strip_name("/strip/name", [strip_id, name])
            state._on_strip_gain("/strip/gain", [strip_id, gain])
            state._on_strip_pan("/strip/pan_stereo_position", [strip_id, pan])

        # Mute guide track temporarily
        state._on_strip_mute("/strip/mute", [1, 1])

        # Solo vocals for recording
        state._on_strip_solo("/strip/solo", [4, 1])

        # Verify mixing state
        tracks = state.get_all_tracks()
        assert len(tracks) == 4
        assert tracks[1].muted is True
        assert tracks[4].soloed is True
        assert tracks[4].name == "Vocals"
