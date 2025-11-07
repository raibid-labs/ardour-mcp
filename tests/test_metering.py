"""
Tests for metering and level monitoring tools.

Tests all metering-related MCP tools including level monitoring,
phase correlation, loudness metering, and data export.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ardour_mcp.ardour_state import ArdourState, TrackState
from ardour_mcp.tools.metering import MeteringTools


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
        10: TrackState(strip_id=10, name="Reverb Bus", track_type="audio",
                      gain_db=-12.0, pan=0.0, muted=False, soloed=False, rec_enabled=False),
    }

    state.get_track.side_effect = lambda track_id: tracks.get(track_id)
    state.get_all_tracks.return_value = tracks

    return state


@pytest.fixture
def metering_tools(mock_osc_bridge, mock_state):
    """Create MeteringTools instance with mocked dependencies."""
    return MeteringTools(mock_osc_bridge, mock_state)


class TestMeteringToolsInitialization:
    """Test MeteringTools initialization."""

    def test_init(self, mock_osc_bridge, mock_state):
        """Test initialization of MeteringTools."""
        tools = MeteringTools(mock_osc_bridge, mock_state)
        assert tools.osc == mock_osc_bridge
        assert tools.state == mock_state
        assert isinstance(tools._meter_cache, dict)


# ========================================================================
# Level Monitoring Tests
# ========================================================================

class TestGetTrackLevel:
    """Test get_track_level method."""

    @pytest.mark.asyncio
    async def test_get_track_level_success(self, metering_tools):
        """Test successfully getting track level."""
        # Add some meter data to cache
        metering_tools._meter_cache[1] = {
            "peak_db": [-12.5, -13.2],
            "rms_db": [-18.3, -19.1],
        }

        result = await metering_tools.get_track_level(1)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["peak_db"] == [-12.5, -13.2]
        assert result["rms_db"] == [-18.3, -19.1]
        assert result["clipping"] is False
        assert "message" in result

    @pytest.mark.asyncio
    async def test_get_track_level_with_clipping(self, metering_tools):
        """Test getting track level when clipping."""
        # Add meter data with clipping
        metering_tools._meter_cache[1] = {
            "peak_db": [0.5, 0.2],  # Above 0 dBFS = clipping
            "rms_db": [-6.0, -6.5],
        }

        result = await metering_tools.get_track_level(1)

        assert result["success"] is True
        assert result["clipping"] is True
        assert result["peak_db"] == [0.5, 0.2]

    @pytest.mark.asyncio
    async def test_get_track_level_track_not_found(self, metering_tools):
        """Test get track level with invalid track ID."""
        result = await metering_tools.get_track_level(99)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_track_level_no_cached_data(self, metering_tools):
        """Test get track level with no cached meter data."""
        result = await metering_tools.get_track_level(1)

        assert result["success"] is True
        assert result["track_id"] == 1
        # Should return default values
        assert "peak_db" in result
        assert "rms_db" in result


class TestGetMasterLevel:
    """Test get_master_level method."""

    @pytest.mark.asyncio
    async def test_get_master_level_success(self, metering_tools):
        """Test successfully getting master level."""
        # Add meter data for master (-1 is master ID)
        metering_tools._meter_cache[-1] = {
            "peak_db": [-6.5, -6.8],
            "rms_db": [-12.3, -12.9],
        }

        result = await metering_tools.get_master_level()

        assert result["success"] is True
        assert result["peak_db"] == [-6.5, -6.8]
        assert result["rms_db"] == [-12.3, -12.9]
        assert result["clipping"] is False
        assert "message" in result

    @pytest.mark.asyncio
    async def test_get_master_level_with_clipping(self, metering_tools):
        """Test getting master level when clipping."""
        metering_tools._meter_cache[-1] = {
            "peak_db": [0.1, -0.5],
            "rms_db": [-3.0, -4.0],
        }

        result = await metering_tools.get_master_level()

        assert result["success"] is True
        assert result["clipping"] is True


class TestGetBusLevel:
    """Test get_bus_level method."""

    @pytest.mark.asyncio
    async def test_get_bus_level_success(self, metering_tools):
        """Test successfully getting bus level."""
        # Add meter data for bus
        metering_tools._meter_cache[10] = {
            "peak_db": [-18.5, -18.2],
            "rms_db": [-24.3, -24.1],
        }

        result = await metering_tools.get_bus_level(10)

        assert result["success"] is True
        assert result["bus_id"] == 10
        assert result["bus_name"] == "Reverb Bus"
        assert result["peak_db"] == [-18.5, -18.2]
        assert result["rms_db"] == [-24.3, -24.1]
        assert result["clipping"] is False

    @pytest.mark.asyncio
    async def test_get_bus_level_bus_not_found(self, metering_tools):
        """Test get bus level with invalid bus ID."""
        result = await metering_tools.get_bus_level(99)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestMonitorLevels:
    """Test monitor_levels method."""

    @pytest.mark.asyncio
    async def test_monitor_levels_success(self, metering_tools, monkeypatch):
        """Test successfully monitoring levels."""
        # Mock get_track_level to return consistent data
        call_count = 0

        async def mock_get_track_level(track_id):
            nonlocal call_count
            call_count += 1
            return {
                "success": True,
                "track_id": track_id,
                "peak_db": [-10.0, -11.0],
                "rms_db": [-16.0, -17.0],
                "clipping": False,
            }

        metering_tools.get_track_level = mock_get_track_level

        result = await metering_tools.monitor_levels([1, 2], duration=0.3)

        assert result["success"] is True
        assert set(result["track_ids"]) == {1, 2}
        assert result["duration"] > 0
        assert result["samples"] > 0
        assert 1 in result["data"]
        assert 2 in result["data"]

        # Check statistics for track 1
        track1_stats = result["data"][1]
        assert track1_stats["track_id"] == 1
        assert track1_stats["track_name"] == "Vocals"
        assert "peak_max" in track1_stats
        assert "peak_min" in track1_stats
        assert "peak_avg" in track1_stats
        assert "rms_avg" in track1_stats
        assert "clipping_events" in track1_stats

    @pytest.mark.asyncio
    async def test_monitor_levels_no_valid_tracks(self, metering_tools):
        """Test monitoring with no valid tracks."""
        result = await metering_tools.monitor_levels([99, 98], duration=0.1)

        assert result["success"] is False
        assert "No valid tracks" in result["error"]

    @pytest.mark.asyncio
    async def test_monitor_levels_partial_valid(self, metering_tools, monkeypatch):
        """Test monitoring with some invalid tracks."""
        async def mock_get_track_level(track_id):
            return {
                "success": True,
                "track_id": track_id,
                "peak_db": [-10.0, -11.0],
                "rms_db": [-16.0, -17.0],
                "clipping": False,
            }

        metering_tools.get_track_level = mock_get_track_level

        result = await metering_tools.monitor_levels([1, 99], duration=0.2)

        assert result["success"] is True
        assert result["track_ids"] == [1]  # Only valid track


# ========================================================================
# Phase & Correlation Tests
# ========================================================================

class TestGetPhaseCorrelation:
    """Test get_phase_correlation method."""

    @pytest.mark.asyncio
    async def test_get_phase_correlation_success(self, metering_tools):
        """Test successfully getting phase correlation."""
        # Add correlation data to cache
        metering_tools._meter_cache[1] = {
            "correlation": 0.85,
        }

        result = await metering_tools.get_phase_correlation(1)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert result["correlation"] == 0.85
        assert result["phase_issue"] is False

    @pytest.mark.asyncio
    async def test_get_phase_correlation_with_issue(self, metering_tools):
        """Test getting phase correlation with phase issue."""
        metering_tools._meter_cache[1] = {
            "correlation": -0.7,  # Significant phase problem
        }

        result = await metering_tools.get_phase_correlation(1)

        assert result["success"] is True
        assert result["correlation"] == -0.7
        assert result["phase_issue"] is True

    @pytest.mark.asyncio
    async def test_get_phase_correlation_track_not_found(self, metering_tools):
        """Test get phase correlation with invalid track ID."""
        result = await metering_tools.get_phase_correlation(99)

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_phase_correlation_no_cached_data(self, metering_tools):
        """Test get phase correlation with no cached data."""
        result = await metering_tools.get_phase_correlation(1)

        assert result["success"] is True
        # Should default to 1.0 (perfect correlation)
        assert result["correlation"] == 1.0
        assert result["phase_issue"] is False


class TestGetMasterPhaseCorrelation:
    """Test get_master_phase_correlation method."""

    @pytest.mark.asyncio
    async def test_get_master_phase_correlation_success(self, metering_tools):
        """Test successfully getting master phase correlation."""
        metering_tools._meter_cache[-1] = {
            "correlation": 0.92,
        }

        result = await metering_tools.get_master_phase_correlation()

        assert result["success"] is True
        assert result["correlation"] == 0.92
        assert result["phase_issue"] is False

    @pytest.mark.asyncio
    async def test_get_master_phase_correlation_with_issue(self, metering_tools):
        """Test master phase correlation with issue."""
        metering_tools._meter_cache[-1] = {
            "correlation": -0.6,
        }

        result = await metering_tools.get_master_phase_correlation()

        assert result["success"] is True
        assert result["phase_issue"] is True


class TestDetectPhaseIssues:
    """Test detect_phase_issues method."""

    @pytest.mark.asyncio
    async def test_detect_phase_issues_found(self, metering_tools, monkeypatch):
        """Test detecting phase issues in tracks."""
        # Mock get_phase_correlation to return issues for some tracks
        async def mock_get_phase_correlation(track_id):
            if track_id == 3:
                return {
                    "success": True,
                    "track_id": track_id,
                    "track_name": "Bass",
                    "correlation": -0.7,
                    "phase_issue": True,
                }
            else:
                return {
                    "success": True,
                    "track_id": track_id,
                    "track_name": f"Track {track_id}",
                    "correlation": 0.9,
                    "phase_issue": False,
                }

        metering_tools.get_phase_correlation = mock_get_phase_correlation

        result = await metering_tools.detect_phase_issues()

        assert result["success"] is True
        assert result["tracks_analyzed"] == 4
        assert result["issues_found"] == 1
        assert len(result["problem_tracks"]) == 1
        assert result["problem_tracks"][0]["track_id"] == 3
        assert result["problem_tracks"][0]["correlation"] == -0.7

    @pytest.mark.asyncio
    async def test_detect_phase_issues_none_found(self, metering_tools, monkeypatch):
        """Test detecting phase issues when none exist."""
        async def mock_get_phase_correlation(track_id):
            return {
                "success": True,
                "track_id": track_id,
                "track_name": f"Track {track_id}",
                "correlation": 0.95,
                "phase_issue": False,
            }

        metering_tools.get_phase_correlation = mock_get_phase_correlation

        result = await metering_tools.detect_phase_issues()

        assert result["success"] is True
        assert result["issues_found"] == 0
        assert len(result["problem_tracks"]) == 0


# ========================================================================
# Loudness Metering Tests
# ========================================================================

class TestAnalyzeLoudness:
    """Test analyze_loudness method."""

    @pytest.mark.asyncio
    async def test_analyze_loudness_track(self, metering_tools):
        """Test analyzing loudness for a track."""
        metering_tools._meter_cache[1] = {
            "rms_db": [-15.0, -15.5],
        }

        result = await metering_tools.analyze_loudness(track_id=1)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["track_name"] == "Vocals"
        assert "integrated_lufs" in result
        assert "loudness_range_lu" in result
        assert "short_term_lufs" in result
        assert "momentary_lufs" in result
        assert "note" in result  # Indicates estimated values

    @pytest.mark.asyncio
    async def test_analyze_loudness_master(self, metering_tools):
        """Test analyzing loudness for master bus."""
        metering_tools._meter_cache[-1] = {
            "rms_db": [-12.0, -12.5],
        }

        result = await metering_tools.analyze_loudness(track_id=None)

        assert result["success"] is True
        assert result["track_id"] is None
        assert result["track_name"] == "Master"
        assert "integrated_lufs" in result

    @pytest.mark.asyncio
    async def test_analyze_loudness_track_not_found(self, metering_tools):
        """Test analyzing loudness with invalid track ID."""
        result = await metering_tools.analyze_loudness(track_id=99)

        assert result["success"] is False
        assert "not found" in result["error"]


class TestGetIntegratedLoudness:
    """Test get_integrated_loudness method."""

    @pytest.mark.asyncio
    async def test_get_integrated_loudness_success(self, metering_tools, monkeypatch):
        """Test successfully getting integrated loudness."""
        # Mock analyze_loudness
        async def mock_analyze_loudness(track_id):
            return {
                "success": True,
                "integrated_lufs": -16.5,
                "loudness_range_lu": 8.0,
            }

        metering_tools.analyze_loudness = mock_analyze_loudness

        result = await metering_tools.get_integrated_loudness()

        assert result["success"] is True
        assert result["integrated_lufs"] == -16.5
        assert result["target_streaming"] == -14.0
        assert result["difference_from_target"] == -2.5  # 2.5 dB quieter than target

    @pytest.mark.asyncio
    async def test_get_integrated_loudness_above_target(self, metering_tools, monkeypatch):
        """Test integrated loudness above streaming target."""
        async def mock_analyze_loudness(track_id):
            return {
                "success": True,
                "integrated_lufs": -11.0,
            }

        metering_tools.analyze_loudness = mock_analyze_loudness

        result = await metering_tools.get_integrated_loudness()

        assert result["success"] is True
        assert result["difference_from_target"] == 3.0  # 3 dB louder than target


class TestGetLoudnessRange:
    """Test get_loudness_range method."""

    @pytest.mark.asyncio
    async def test_get_loudness_range_dynamic(self, metering_tools, monkeypatch):
        """Test loudness range for dynamic material."""
        async def mock_analyze_loudness(track_id):
            return {
                "success": True,
                "loudness_range_lu": 16.0,
            }

        metering_tools.analyze_loudness = mock_analyze_loudness

        result = await metering_tools.get_loudness_range()

        assert result["success"] is True
        assert result["loudness_range_lu"] == 16.0
        assert result["dynamic_range_category"] == "very dynamic"

    @pytest.mark.asyncio
    async def test_get_loudness_range_compressed(self, metering_tools, monkeypatch):
        """Test loudness range for compressed material."""
        async def mock_analyze_loudness(track_id):
            return {
                "success": True,
                "loudness_range_lu": 3.5,
            }

        metering_tools.analyze_loudness = mock_analyze_loudness

        result = await metering_tools.get_loudness_range()

        assert result["success"] is True
        assert result["loudness_range_lu"] == 3.5
        assert result["dynamic_range_category"] == "compressed"

    @pytest.mark.asyncio
    async def test_get_loudness_range_moderate(self, metering_tools, monkeypatch):
        """Test loudness range for moderate material."""
        async def mock_analyze_loudness(track_id):
            return {
                "success": True,
                "loudness_range_lu": 8.0,
            }

        metering_tools.analyze_loudness = mock_analyze_loudness

        result = await metering_tools.get_loudness_range()

        assert result["success"] is True
        assert result["dynamic_range_category"] == "moderate"


# ========================================================================
# Analysis & Export Tests
# ========================================================================

class TestDetectClipping:
    """Test detect_clipping method."""

    @pytest.mark.asyncio
    async def test_detect_clipping_clipping_detected(self, metering_tools, monkeypatch):
        """Test detecting clipping."""
        async def mock_get_track_level(track_id):
            return {
                "success": True,
                "track_id": track_id,
                "track_name": "Vocals",
                "peak_db": [0.5, 0.2],
                "clipping": True,
            }

        metering_tools.get_track_level = mock_get_track_level

        result = await metering_tools.detect_clipping(1)

        assert result["success"] is True
        assert result["is_clipping"] is True
        assert result["headroom_db"] == [-0.5, -0.2]
        assert "CLIPPING" in result["recommendation"]

    @pytest.mark.asyncio
    async def test_detect_clipping_low_headroom(self, metering_tools, monkeypatch):
        """Test detecting low headroom."""
        async def mock_get_track_level(track_id):
            return {
                "success": True,
                "track_id": track_id,
                "track_name": "Vocals",
                "peak_db": [-2.0, -1.5],
                "clipping": False,
            }

        metering_tools.get_track_level = mock_get_track_level

        result = await metering_tools.detect_clipping(1)

        assert result["success"] is True
        assert result["is_clipping"] is False
        assert result["headroom_db"] == [2.0, 1.5]
        assert "Low headroom" in result["recommendation"]

    @pytest.mark.asyncio
    async def test_detect_clipping_good_headroom(self, metering_tools, monkeypatch):
        """Test detecting good headroom."""
        async def mock_get_track_level(track_id):
            return {
                "success": True,
                "track_id": track_id,
                "track_name": "Vocals",
                "peak_db": [-8.0, -7.5],
                "clipping": False,
            }

        metering_tools.get_track_level = mock_get_track_level

        result = await metering_tools.detect_clipping(1)

        assert result["success"] is True
        assert result["is_clipping"] is False
        assert "Good headroom" in result["recommendation"]


class TestExportLevelData:
    """Test export_level_data method."""

    @pytest.mark.asyncio
    async def test_export_level_data_success(self, metering_tools, monkeypatch):
        """Test successfully exporting level data."""
        # Mock monitor_levels
        async def mock_monitor_levels(track_ids, duration):
            return {
                "success": True,
                "track_ids": [1, 2],
                "duration": 0.3,
                "samples": 3,
                "data": {
                    1: {
                        "track_name": "Vocals",
                        "peak_max": [-10.0, -11.0],
                        "peak_min": [-15.0, -16.0],
                        "peak_avg": [-12.5, -13.5],
                        "rms_avg": [-18.0, -19.0],
                        "clipping_events": 0,
                    },
                    2: {
                        "track_name": "Guitar",
                        "peak_max": [-8.0, -9.0],
                        "peak_min": [-12.0, -13.0],
                        "peak_avg": [-10.0, -11.0],
                        "rms_avg": [-16.0, -17.0],
                        "clipping_events": 1,
                    },
                },
            }

        metering_tools.monitor_levels = mock_monitor_levels

        result = await metering_tools.export_level_data([1, 2], duration=0.3)

        assert result["success"] is True
        assert result["track_ids"] == [1, 2]
        assert result["duration"] == 0.3
        assert result["samples"] == 3
        assert "sample_rate" in result
        assert result["format_version"] == "1.0"
        assert "data" in result

        # Check exported data structure
        assert 1 in result["data"]
        assert 2 in result["data"]
        track1_data = result["data"][1]
        assert track1_data["track_id"] == 1
        assert track1_data["track_name"] == "Vocals"
        assert "statistics" in track1_data

    @pytest.mark.asyncio
    async def test_export_level_data_no_valid_tracks(self, metering_tools, monkeypatch):
        """Test exporting with no valid tracks."""
        async def mock_monitor_levels(track_ids, duration):
            return {
                "success": False,
                "error": "No valid tracks to monitor",
            }

        metering_tools.monitor_levels = mock_monitor_levels

        result = await metering_tools.export_level_data([99], duration=0.1)

        assert result["success"] is False


# ========================================================================
# Feedback Handler Tests
# ========================================================================

class TestFeedbackHandlers:
    """Test OSC feedback handlers."""

    def test_on_strip_meter(self, metering_tools):
        """Test /strip/meter feedback handler."""
        args = [1, -12.5, -13.2, -18.3, -19.1]
        metering_tools._on_strip_meter("/strip/meter", args)

        assert 1 in metering_tools._meter_cache
        meter_data = metering_tools._meter_cache[1]
        assert meter_data["peak_db"] == [-12.5, -13.2]
        assert meter_data["rms_db"] == [-18.3, -19.1]
        assert "timestamp" in meter_data

    def test_on_strip_meter_insufficient_args(self, metering_tools):
        """Test /strip/meter with insufficient arguments."""
        args = [1, -12.5]  # Not enough args
        metering_tools._on_strip_meter("/strip/meter", args)

        # Should not crash or add invalid data
        assert 1 not in metering_tools._meter_cache

    def test_on_master_meter(self, metering_tools):
        """Test /master/meter feedback handler."""
        args = [-6.5, -6.8, -12.3, -12.9]
        metering_tools._on_master_meter("/master/meter", args)

        assert -1 in metering_tools._meter_cache
        meter_data = metering_tools._meter_cache[-1]
        assert meter_data["peak_db"] == [-6.5, -6.8]
        assert meter_data["rms_db"] == [-12.3, -12.9]

    def test_on_master_meter_insufficient_args(self, metering_tools):
        """Test /master/meter with insufficient arguments."""
        args = [-6.5]  # Not enough args
        metering_tools._on_master_meter("/master/meter", args)

        # Should not crash
        assert -1 not in metering_tools._meter_cache


# ========================================================================
# Edge Case Tests
# ========================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_monitor_levels_zero_duration(self, metering_tools):
        """Test monitoring with very short duration."""
        async def mock_get_track_level(track_id):
            return {
                "success": True,
                "track_id": track_id,
                "peak_db": [-10.0, -11.0],
                "rms_db": [-16.0, -17.0],
                "clipping": False,
            }

        metering_tools.get_track_level = mock_get_track_level

        # Very short duration should still collect at least 1 sample
        result = await metering_tools.monitor_levels([1], duration=0.1)

        assert result["success"] is True
        assert result["samples"] >= 1

    @pytest.mark.asyncio
    async def test_get_track_level_extreme_values(self, metering_tools):
        """Test track level with extreme dB values."""
        metering_tools._meter_cache[1] = {
            "peak_db": [100.0, -193.0],  # Extreme values
            "rms_db": [50.0, -200.0],
        }

        result = await metering_tools.get_track_level(1)

        assert result["success"] is True
        assert result["peak_db"] == [100.0, -193.0]
        # Clipping detection should work even with extreme values
        assert result["clipping"] is True  # 100.0 >= 0

    @pytest.mark.asyncio
    async def test_phase_correlation_boundary_values(self, metering_tools):
        """Test phase correlation with boundary values."""
        # Test correlation exactly at -0.5 (boundary for phase_issue)
        metering_tools._meter_cache[1] = {"correlation": -0.5}

        result = await metering_tools.get_phase_correlation(1)

        assert result["success"] is True
        # -0.5 should NOT be considered a phase issue (< -0.5 is the condition)
        assert result["phase_issue"] is False

        # Test just below boundary (-0.51 should trigger issue)
        metering_tools._meter_cache[1] = {"correlation": -0.51}
        result = await metering_tools.get_phase_correlation(1)
        assert result["phase_issue"] is True
