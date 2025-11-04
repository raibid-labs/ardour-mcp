"""
State management for Ardour session.

This module maintains a cached representation of Ardour's current state,
updated via OSC feedback. This allows fast queries without round-trip
OSC communication.
"""

import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TransportState:
    """Current transport state."""

    playing: bool = False
    recording: bool = False
    frame: int = 0
    tempo: float = 120.0
    time_signature: Tuple[int, int] = (4, 4)
    loop_enabled: bool = False


@dataclass
class TrackState:
    """State of a single track."""

    strip_id: int
    name: str = ""
    track_type: str = "audio"  # "audio" or "midi"
    muted: bool = False
    soloed: bool = False
    rec_enabled: bool = False
    gain_db: float = 0.0
    pan: float = 0.0  # -1.0 (left) to 1.0 (right)
    hidden: bool = False


@dataclass
class SessionState:
    """Complete Ardour session state."""

    name: str = ""
    path: str = ""
    sample_rate: int = 48000
    tracks: Dict[int, TrackState] = field(default_factory=dict)
    markers: List[Tuple[str, int]] = field(default_factory=list)
    transport: TransportState = field(default_factory=TransportState)
    dirty: bool = False  # Session modified since last save


class ArdourState:
    """
    Thread-safe state cache for Ardour session.

    Maintains current Ardour state, updated via OSC feedback.
    Provides fast, synchronous access to state information.
    Integrates with OSC bridge to receive automatic state updates.
    """

    def __init__(self) -> None:
        """Initialize empty state."""
        self._lock = threading.RLock()
        self._state = SessionState()
        logger.info("Ardour state cache initialized")

    def register_feedback_handlers(self, osc_bridge: Any) -> None:
        """
        Register OSC feedback handlers with the bridge.

        Sets up handlers for all Ardour feedback messages to
        automatically update the state cache.

        Args:
            osc_bridge: ArdourOSCBridge instance to register handlers with
        """
        # Transport feedback
        osc_bridge.register_feedback_handler("/transport_frame", self._on_transport_frame)
        osc_bridge.register_feedback_handler("/transport_speed", self._on_transport_speed)
        osc_bridge.register_feedback_handler("/record_enabled", self._on_record_enabled)
        osc_bridge.register_feedback_handler("/tempo", self._on_tempo)
        osc_bridge.register_feedback_handler("/time_signature", self._on_time_signature)
        osc_bridge.register_feedback_handler("/loop_toggle", self._on_loop_toggle)

        # Session feedback
        osc_bridge.register_feedback_handler("/session_name", self._on_session_name)
        osc_bridge.register_feedback_handler("/sample_rate", self._on_sample_rate)
        osc_bridge.register_feedback_handler("/dirty", self._on_dirty)

        # Track feedback (strip messages)
        osc_bridge.register_feedback_handler("/strip/name", self._on_strip_name)
        osc_bridge.register_feedback_handler("/strip/gain", self._on_strip_gain)
        osc_bridge.register_feedback_handler("/strip/pan_stereo_position", self._on_strip_pan)
        osc_bridge.register_feedback_handler("/strip/mute", self._on_strip_mute)
        osc_bridge.register_feedback_handler("/strip/solo", self._on_strip_solo)
        osc_bridge.register_feedback_handler("/strip/recenable", self._on_strip_recenable)

        logger.info("Registered OSC feedback handlers for state updates")

    # Feedback handler methods
    def _on_transport_frame(self, address: str, args: List[Any]) -> None:
        """Handle transport frame updates."""
        if args:
            self.update_transport(frame=args[0])

    def _on_transport_speed(self, address: str, args: List[Any]) -> None:
        """Handle transport speed updates."""
        if args:
            speed = args[0]
            # Speed: 0.0 = stopped, 1.0 = playing forward
            self.update_transport(playing=speed > 0.0)

    def _on_record_enabled(self, address: str, args: List[Any]) -> None:
        """Handle record enable updates."""
        if args:
            self.update_transport(recording=bool(args[0]))

    def _on_tempo(self, address: str, args: List[Any]) -> None:
        """Handle tempo updates."""
        if args:
            self.update_transport(tempo=float(args[0]))

    def _on_time_signature(self, address: str, args: List[Any]) -> None:
        """Handle time signature updates."""
        if len(args) >= 2:
            with self._lock:
                self._state.transport.time_signature = (int(args[0]), int(args[1]))
                logger.debug(f"Time signature updated: {args[0]}/{args[1]}")

    def _on_loop_toggle(self, address: str, args: List[Any]) -> None:
        """Handle loop toggle updates."""
        if args:
            with self._lock:
                self._state.transport.loop_enabled = bool(args[0])

    def _on_session_name(self, address: str, args: List[Any]) -> None:
        """Handle session name updates."""
        if args:
            with self._lock:
                self._state.name = str(args[0])
                logger.debug(f"Session name: {args[0]}")

    def _on_sample_rate(self, address: str, args: List[Any]) -> None:
        """Handle sample rate updates."""
        if args:
            with self._lock:
                self._state.sample_rate = int(args[0])
                logger.debug(f"Sample rate: {args[0]}")

    def _on_dirty(self, address: str, args: List[Any]) -> None:
        """Handle session dirty flag updates."""
        if args:
            with self._lock:
                self._state.dirty = bool(args[0])

    def _on_strip_name(self, address: str, args: List[Any]) -> None:
        """Handle track name updates."""
        if len(args) >= 2:
            strip_id, name = int(args[0]), str(args[1])
            self.update_track(strip_id, name=name)

    def _on_strip_gain(self, address: str, args: List[Any]) -> None:
        """Handle track gain updates."""
        if len(args) >= 2:
            strip_id, gain = int(args[0]), float(args[1])
            self.update_track(strip_id, gain_db=gain)

    def _on_strip_pan(self, address: str, args: List[Any]) -> None:
        """Handle track pan updates."""
        if len(args) >= 2:
            strip_id, pan = int(args[0]), float(args[1])
            self.update_track(strip_id, pan=pan)

    def _on_strip_mute(self, address: str, args: List[Any]) -> None:
        """Handle track mute updates."""
        if len(args) >= 2:
            strip_id, muted = int(args[0]), bool(args[1])
            self.update_track(strip_id, muted=muted)

    def _on_strip_solo(self, address: str, args: List[Any]) -> None:
        """Handle track solo updates."""
        if len(args) >= 2:
            strip_id, soloed = int(args[0]), bool(args[1])
            self.update_track(strip_id, soloed=soloed)

    def _on_strip_recenable(self, address: str, args: List[Any]) -> None:
        """Handle track record enable updates."""
        if len(args) >= 2:
            strip_id, rec_enabled = int(args[0]), bool(args[1])
            self.update_track(strip_id, rec_enabled=rec_enabled)

    def update_transport(
        self,
        playing: Optional[bool] = None,
        recording: Optional[bool] = None,
        frame: Optional[int] = None,
        tempo: Optional[float] = None,
    ) -> None:
        """
        Update transport state.

        Args:
            playing: Playback state
            recording: Recording state
            frame: Current frame position
            tempo: Current tempo (BPM)
        """
        with self._lock:
            if playing is not None:
                self._state.transport.playing = playing
            if recording is not None:
                self._state.transport.recording = recording
            if frame is not None:
                self._state.transport.frame = frame
            if tempo is not None:
                self._state.transport.tempo = tempo
            logger.debug(f"Transport state updated: {self._state.transport}")

    def update_track(self, strip_id: int, **kwargs: Any) -> None:
        """
        Update track state.

        Args:
            strip_id: Track/strip ID (1-based)
            **kwargs: Track properties to update
        """
        with self._lock:
            if strip_id not in self._state.tracks:
                self._state.tracks[strip_id] = TrackState(strip_id=strip_id)

            track = self._state.tracks[strip_id]
            for key, value in kwargs.items():
                if hasattr(track, key):
                    setattr(track, key, value)

            logger.debug(f"Track {strip_id} state updated: {track}")

    def get_transport(self) -> TransportState:
        """
        Get current transport state.

        Returns:
            Current transport state
        """
        with self._lock:
            return self._state.transport

    def get_track(self, strip_id: int) -> Optional[TrackState]:
        """
        Get state of specific track.

        Args:
            strip_id: Track/strip ID (1-based)

        Returns:
            Track state if exists, None otherwise
        """
        with self._lock:
            return self._state.tracks.get(strip_id)

    def get_all_tracks(self) -> Dict[int, TrackState]:
        """
        Get all track states.

        Returns:
            Dictionary of strip_id -> TrackState
        """
        with self._lock:
            return dict(self._state.tracks)

    def get_session_info(self) -> SessionState:
        """
        Get complete session state.

        Returns:
            Current session state
        """
        with self._lock:
            return self._state

    def clear(self) -> None:
        """
        Clear all cached state.

        Useful when disconnecting or on errors.
        """
        with self._lock:
            self._state = SessionState()
            logger.info("State cache cleared")
