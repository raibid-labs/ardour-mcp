"""
State management for Ardour session.

This module maintains a cached representation of Ardour's current state,
updated via OSC feedback. This allows fast queries without round-trip
OSC communication.
"""

import logging
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

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
    """

    def __init__(self) -> None:
        """Initialize empty state."""
        self._lock = threading.RLock()
        self._state = SessionState()
        logger.info("Ardour state cache initialized")

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

    def update_track(
        self, strip_id: int, **kwargs: Any
    ) -> None:
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


# TODO: Remove this when implementation begins
Any = object  # Type annotation placeholder
