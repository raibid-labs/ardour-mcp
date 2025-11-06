#!/usr/bin/env python3
"""Quick OSC connection test."""

import asyncio
import sys

from ardour_mcp.osc_bridge import ArdourOSCBridge


async def test_connection():
    """Test basic OSC connection to Ardour."""
    bridge = ArdourOSCBridge()
    try:
        await bridge.connect()
        print("✅ Connected to Ardour OSC")

        # Send a simple command
        success = bridge.send_command("/transport_stop")
        if success:
            print("✅ Successfully sent OSC command")
        else:
            print("⚠️  Failed to send OSC command")

        # Get connection info
        info = bridge.get_connection_info()
        print(f"Connection info: {info}")

        await bridge.disconnect()
        print("✅ Disconnected from Ardour")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)
