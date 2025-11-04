"""
Tests for OSC bridge functionality.

Tests bidirectional OSC communication with Ardour.
"""

import asyncio
from typing import List

import pytest
from pythonosc import udp_client

from ardour_mcp.osc_bridge import ArdourOSCBridge, OSCConnectionError


@pytest.fixture
def bridge():
    """Create an OSC bridge instance for testing."""
    return ArdourOSCBridge(ardour_host="localhost", ardour_port=3819, feedback_port=3820)


@pytest.fixture
async def connected_bridge():
    """Create and connect an OSC bridge instance."""
    bridge = ArdourOSCBridge(
        ardour_host="localhost",
        ardour_port=3819,
        feedback_port=3821,  # Different port
    )
    await bridge.connect()
    yield bridge
    await bridge.disconnect()


class TestOSCBridgeInitialization:
    """Test OSC bridge initialization."""

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        bridge = ArdourOSCBridge()
        assert bridge.ardour_host == "localhost"
        assert bridge.ardour_port == 3819
        assert bridge.feedback_port == 3820
        assert not bridge.is_connected()

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        bridge = ArdourOSCBridge(ardour_host="192.168.1.100", ardour_port=9000, feedback_port=9001)
        assert bridge.ardour_host == "192.168.1.100"
        assert bridge.ardour_port == 9000
        assert bridge.feedback_port == 9001

    def test_init_state(self, bridge):
        """Test initial state of bridge."""
        assert bridge.client is None
        assert bridge.server is None
        assert bridge.server_thread is None
        assert not bridge.is_connected()
        assert len(bridge.feedback_handlers) == 0


class TestOSCBridgeConnection:
    """Test OSC bridge connection management."""

    @pytest.mark.asyncio
    async def test_connect_success(self, bridge):
        """Test successful connection."""
        await bridge.connect()
        assert bridge.is_connected()
        assert bridge.client is not None
        assert bridge.server is not None
        assert bridge.server_thread is not None
        assert bridge.server_thread.is_alive()
        await bridge.disconnect()

    @pytest.mark.asyncio
    async def test_connect_already_connected(self, connected_bridge):
        """Test connecting when already connected."""
        # Should return True and log warning
        result = await connected_bridge.connect()
        assert result is True
        assert connected_bridge.is_connected()

    @pytest.mark.asyncio
    async def test_connect_port_in_use(self):
        """Test connection when feedback port is in use."""
        bridge1 = ArdourOSCBridge(feedback_port=3822)
        await bridge1.connect()

        bridge2 = ArdourOSCBridge(feedback_port=3822)  # Same port
        with pytest.raises(OSCConnectionError):
            await bridge2.connect()

        await bridge1.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect_when_connected(self, connected_bridge):
        """Test disconnecting when connected."""
        await connected_bridge.disconnect()
        assert not connected_bridge.is_connected()
        assert connected_bridge.client is None
        assert connected_bridge.server is None

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self, bridge):
        """Test disconnecting when not connected."""
        # Should not raise exception, just log warning
        await bridge.disconnect()
        assert not bridge.is_connected()

    @pytest.mark.asyncio
    async def test_connection_info(self, connected_bridge):
        """Test getting connection information."""
        info = connected_bridge.get_connection_info()
        assert info["connected"] is True
        assert info["ardour_host"] == "localhost"
        assert info["ardour_port"] == 3819
        assert info["feedback_port"] == 3821
        assert "handlers_registered" in info


class TestOSCBridgeCommands:
    """Test sending OSC commands."""

    @pytest.mark.asyncio
    async def test_send_command_when_connected(self, connected_bridge):
        """Test sending command when connected."""
        result = connected_bridge.send_command("/transport_play")
        assert result is True

    @pytest.mark.asyncio
    async def test_send_command_with_args(self, connected_bridge):
        """Test sending command with arguments."""
        result = connected_bridge.send_command("/strip/gain", 1, -6.0)
        assert result is True

    def test_send_command_when_not_connected(self, bridge):
        """Test sending command when not connected."""
        result = bridge.send_command("/transport_play")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_multiple_commands(self, connected_bridge):
        """Test sending multiple commands in sequence."""
        commands = [
            ("/transport_play", ()),
            ("/transport_stop", ()),
            ("/strip/gain", (1, -6.0)),
            ("/strip/mute", (1, 1)),
        ]

        for address, args in commands:
            result = connected_bridge.send_command(address, *args)
            assert result is True


class TestOSCBridgeFeedback:
    """Test receiving OSC feedback."""

    @pytest.mark.asyncio
    async def test_register_feedback_handler(self, connected_bridge):
        """Test registering a feedback handler."""
        handler_called = []

        def handler(address: str, args: List):
            handler_called.append((address, args))

        connected_bridge.register_feedback_handler("/transport_frame", handler)
        assert "/transport_frame" in connected_bridge.feedback_handlers
        assert len(connected_bridge.feedback_handlers["/transport_frame"]) == 1

    @pytest.mark.asyncio
    async def test_receive_feedback(self, connected_bridge):
        """Test receiving feedback messages."""
        received_messages = []

        def handler(address: str, args: List):
            received_messages.append((address, args))

        # Register handler
        connected_bridge.register_feedback_handler("/test_feedback", handler)

        # Simulate sending feedback to ourselves
        test_client = udp_client.SimpleUDPClient("localhost", 3821)
        test_client.send_message("/test_feedback", [42, "test"])

        # Wait for message to be received
        await asyncio.sleep(0.1)

        # Verify handler was called
        assert len(received_messages) == 1
        assert received_messages[0][0] == "/test_feedback"
        assert received_messages[0][1] == [42, "test"]

    @pytest.mark.asyncio
    async def test_multiple_handlers_same_address(self, connected_bridge):
        """Test multiple handlers for same address."""
        results1 = []
        results2 = []

        def handler1(address: str, args: List):
            results1.append(args)

        def handler2(address: str, args: List):
            results2.append(args)

        connected_bridge.register_feedback_handler("/test", handler1)
        connected_bridge.register_feedback_handler("/test", handler2)

        # Send test message
        test_client = udp_client.SimpleUDPClient("localhost", 3821)
        test_client.send_message("/test", [123])

        await asyncio.sleep(0.1)

        # Both handlers should be called
        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0] == [123]
        assert results2[0] == [123]

    @pytest.mark.asyncio
    async def test_unregister_feedback_handler(self, connected_bridge):
        """Test unregistering feedback handlers."""
        handler_called = []

        def handler(address: str, args: List):
            handler_called.append((address, args))

        # Register and then unregister
        connected_bridge.register_feedback_handler("/test", handler)
        assert "/test" in connected_bridge.feedback_handlers

        connected_bridge.unregister_feedback_handler("/test")
        assert "/test" not in connected_bridge.feedback_handlers

    @pytest.mark.asyncio
    async def test_feedback_handler_error_handling(self, connected_bridge):
        """Test that errors in handlers don't crash the bridge."""

        def failing_handler(address: str, args: List):
            raise ValueError("Intentional test error")

        connected_bridge.register_feedback_handler("/test_error", failing_handler)

        # Send message that will trigger error
        test_client = udp_client.SimpleUDPClient("localhost", 3821)
        test_client.send_message("/test_error", [1, 2, 3])

        await asyncio.sleep(0.1)

        # Bridge should still be operational
        assert connected_bridge.is_connected()


class TestOSCBridgeEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_send_empty_command(self, connected_bridge):
        """Test sending command with no arguments."""
        result = connected_bridge.send_command("/transport_play")
        assert result is True

    @pytest.mark.asyncio
    async def test_send_command_various_types(self, connected_bridge):
        """Test sending commands with various argument types."""
        # Integer
        result = connected_bridge.send_command("/test", 42)
        assert result is True

        # Float
        result = connected_bridge.send_command("/test", 3.14)
        assert result is True

        # String
        result = connected_bridge.send_command("/test", "hello")
        assert result is True

        # Mixed types
        result = connected_bridge.send_command("/test", 1, 2.5, "test")
        assert result is True

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, connected_bridge):
        """Test concurrent send operations."""

        async def send_many():
            for i in range(10):
                connected_bridge.send_command(f"/test/{i}", i)
                await asyncio.sleep(0.01)

        # Run multiple concurrent sends
        await asyncio.gather(send_many(), send_many(), send_many())

        # Bridge should still be operational
        assert connected_bridge.is_connected()

    @pytest.mark.asyncio
    async def test_reconnection(self, bridge):
        """Test connecting, disconnecting, and reconnecting."""
        # Connect
        await bridge.connect()
        assert bridge.is_connected()

        # Disconnect
        await bridge.disconnect()
        assert not bridge.is_connected()

        # Reconnect
        await bridge.connect()
        assert bridge.is_connected()

        # Cleanup
        await bridge.disconnect()


class TestOSCBridgeThreadSafety:
    """Test thread safety of the bridge."""

    @pytest.mark.asyncio
    async def test_thread_safe_connection_check(self, connected_bridge):
        """Test that connection check is thread-safe."""
        import threading

        results = []

        def check_connection():
            for _ in range(100):
                results.append(connected_bridge.is_connected())

        # Run multiple threads checking connection
        threads = [threading.Thread(target=check_connection) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All checks should return True
        assert all(results)
        assert len(results) == 500  # 5 threads * 100 checks
