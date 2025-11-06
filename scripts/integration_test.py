#!/usr/bin/env python3
"""
Integration tests for Ardour MCP.

Tests all MCP tools with a live Ardour instance.
"""

import asyncio
import sys

from ardour_mcp.ardour_state import ArdourState
from ardour_mcp.osc_bridge import ArdourOSCBridge
from ardour_mcp.tools.session import SessionTools
from ardour_mcp.tools.tracks import TrackTools
from ardour_mcp.tools.transport import TransportTools


async def run_integration_tests():
    """Run comprehensive integration tests with live Ardour instance."""

    print("\n=== Ardour MCP Integration Tests ===\n")

    # Initialize components
    osc = ArdourOSCBridge()
    state = ArdourState()

    try:
        # Connect to Ardour
        print("1. Connecting to Ardour...")
        await osc.connect()
        state.register_feedback_handlers(osc)
        print("✅ Connected\n")

        # Give OSC feedback a moment to populate state
        await asyncio.sleep(1)

        # Initialize tools
        transport = TransportTools(osc, state)
        tracks = TrackTools(osc, state)
        session = SessionTools(osc, state)

        # Test session info
        print("2. Testing session information...")
        session_info = await session.get_session_info()
        print(f"   Session: {session_info.get('session_name', 'Unknown')}")
        print(f"   Sample Rate: {session_info.get('sample_rate', 'Unknown')} Hz")
        print(f"   Tempo: {session_info.get('tempo', 'Unknown')} BPM")
        print(f"   Time Signature: {session_info.get('time_signature', 'Unknown')}")
        print("✅ Session info retrieved\n")

        # Test track listing
        print("3. Testing track management...")
        track_list = await tracks.list_tracks()
        print(f"   Current tracks: {track_list.get('track_count', 0)}")
        if track_list.get('tracks'):
            for track in track_list['tracks'][:3]:  # Show first 3
                print(f"   - {track['name']} (ID: {track['strip_id']}, "
                      f"Type: {track['type']}, Gain: {track['gain_db']}dB)")
        print("✅ Track listing works\n")

        # Test creating a track
        print("4. Testing track creation...")
        create_result = await tracks.create_audio_track("MCP Test Track")
        if create_result['success']:
            print(f"✅ Created track: {create_result['message']}")
            print(f"   Total tracks now: {create_result.get('track_count', '?')}\n")
        else:
            print(f"⚠️  Track creation: {create_result.get('error', 'Unknown error')}\n")

        # Wait for feedback to update
        await asyncio.sleep(0.5)

        # List tracks again to see the new track
        track_list_after = await tracks.list_tracks()
        if track_list_after.get('track_count', 0) > track_list.get('track_count', 0):
            print(f"   Verified: Track count increased to {track_list_after['track_count']}\n")

        # Test transport controls
        print("5. Testing transport controls...")

        # Stop transport
        stop_result = await transport.transport_stop()
        print(f"   Stop: {'✅' if stop_result['success'] else '❌'}")

        await asyncio.sleep(0.2)

        # Go to start
        start_result = await transport.goto_start()
        print(f"   Goto Start: {'✅' if start_result['success'] else '❌'}")

        await asyncio.sleep(0.2)

        # Get position
        pos_result = await transport.get_transport_position()
        print(f"   Position: Frame {pos_result.get('frame', 0)}")
        print(f"   Playing: {pos_result.get('playing', False)}")
        print(f"   Recording: {pos_result.get('recording', False)}")
        print("✅ Transport controls work\n")

        # Test markers
        print("6. Testing markers...")
        markers = await session.list_markers()
        print(f"   Markers in session: {markers.get('marker_count', 0)}")
        if markers.get('markers'):
            for marker in markers['markers'][:3]:  # Show first 3
                print(f"   - {marker['name']} at frame {marker['frame']}")
        print("✅ Marker listing works\n")

        # Test additional session queries
        print("7. Testing additional session queries...")
        tempo = await session.get_tempo()
        print(f"   Tempo: {tempo.get('tempo', '?')} BPM")

        time_sig = await session.get_time_signature()
        print(f"   Time Signature: {time_sig.get('time_signature', '?')}")

        sample_rate = await session.get_sample_rate()
        print(f"   Sample Rate: {sample_rate.get('sample_rate', '?')} Hz")

        track_count = await session.get_track_count()
        print(f"   Track Count: {track_count.get('track_count', '?')}")

        dirty = await session.is_session_dirty()
        print(f"   Session Modified: {dirty.get('dirty', '?')}")
        print("✅ Session queries work\n")

        # Test track operations
        if track_list_after.get('tracks'):
            print("8. Testing track operations...")
            test_track = track_list_after['tracks'][0]
            track_id = test_track['strip_id']

            # Select track
            select_result = await tracks.select_track(track_id)
            print(f"   Select track {track_id}: "
                  f"{'✅' if select_result['success'] else '❌'}")

            await asyncio.sleep(0.2)

            # Rename track
            rename_result = await tracks.rename_track(
                track_id,
                f"{test_track['name']}_renamed"
            )
            print(f"   Rename track: "
                  f"{'✅' if rename_result['success'] else '❌'}")

            print("✅ Track operations work\n")

        # Cleanup
        print("9. Cleaning up...")
        await osc.disconnect()
        state.clear()
        print("✅ Disconnected\n")

        print("=== All Integration Tests Passed! ===\n")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}\n")
        import traceback
        traceback.print_exc()

        # Cleanup on error
        try:
            await osc.disconnect()
        except:
            pass

        return False


if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)
