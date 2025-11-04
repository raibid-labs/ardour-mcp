"""
OSC Bridge for communicating with Ardour.

This module handles bidirectional OSC communication:
- Sending commands to Ardour (OSC client)
- Receiving feedback from Ardour (OSC server)
"""

import logging
import threading
from typing import Any, Callable, Dict, List, Optional

from pythonosc import dispatcher, osc_server, udp_client

logger = logging.getLogger(__name__)


class OSCConnectionError(Exception):
    """Raised when OSC connection fails."""

    pass


class ArdourOSCBridge:
    """
    Bidirectional OSC bridge for Ardour communication.

    Manages both sending commands to Ardour and receiving
    feedback messages for state synchronization.

    This class handles:
    - Sending OSC commands to Ardour (UDP client)
    - Receiving OSC feedback from Ardour (UDP server in separate thread)
    - Connection lifecycle management
    - Error handling and reconnection
    """

    def __init__(
        self,
        ardour_host: str = "localhost",
        ardour_port: int = 3819,
        feedback_port: int = 3820,
    ) -> None:
        """
        Initialize the OSC bridge.

        Args:
            ardour_host: Host address where Ardour is running
            ardour_port: Port where Ardour's OSC server listens
            feedback_port: Port for receiving feedback from Ardour
        """
        self.ardour_host = ardour_host
        self.ardour_port = ardour_port
        self.feedback_port = feedback_port

        # OSC client for sending commands
        self.client: Optional[udp_client.SimpleUDPClient] = None

        # OSC server for receiving feedback
        self.dispatcher = dispatcher.Dispatcher()
        self.server: Optional[osc_server.ThreadingOSCUDPServer] = None
        self.server_thread: Optional[threading.Thread] = None

        # Connection state
        self._connected = False
        self._lock = threading.Lock()

        # Feedback handlers
        self.feedback_handlers: Dict[str, List[Callable]] = {}

        # Set up default feedback handler for logging
        self.dispatcher.set_default_handler(self._default_feedback_handler)

        logger.info(
            f"OSC Bridge initialized: Ardour at {ardour_host}:{ardour_port}, "
            f"feedback on port {feedback_port}"
        )

    async def connect(self) -> bool:
        """
        Connect to Ardour's OSC server.

        Establishes the OSC client connection and starts the
        feedback server in a background thread.

        Returns:
            True if connection successful, False otherwise

        Raises:
            OSCConnectionError: If connection fails
        """
        with self._lock:
            if self._connected:
                logger.warning("Already connected to Ardour")
                return True

            try:
                logger.info("Connecting to Ardour...")

                # Create OSC client for sending commands
                self.client = udp_client.SimpleUDPClient(self.ardour_host, self.ardour_port)
                logger.debug(f"OSC client created: {self.ardour_host}:{self.ardour_port}")

                # Start OSC server for receiving feedback
                self._start_feedback_server()

                # Test connection by sending /refresh command
                self.send_command("/refresh")
                logger.debug("Sent /refresh command to test connection")

                self._connected = True
                logger.info("Successfully connected to Ardour")
                return True

            except OSError as e:
                error_msg = f"Failed to connect to Ardour: {e}"
                logger.error(error_msg)
                raise OSCConnectionError(error_msg) from e
            except Exception as e:
                error_msg = f"Unexpected error during connection: {e}"
                logger.error(error_msg, exc_info=True)
                raise OSCConnectionError(error_msg) from e

    def _start_feedback_server(self) -> None:
        """
        Start the OSC feedback server in a background thread.

        Raises:
            OSError: If server cannot bind to port
        """
        try:
            # Create server with our dispatcher
            self.server = osc_server.ThreadingOSCUDPServer(
                ("0.0.0.0", self.feedback_port), self.dispatcher
            )
            logger.debug(f"OSC feedback server created on port {self.feedback_port}")

            # Start server in background thread
            self.server_thread = threading.Thread(
                target=self.server.serve_forever, daemon=True, name="OSC-Feedback-Server"
            )
            self.server_thread.start()
            logger.info(f"OSC feedback server started on port {self.feedback_port}")

        except OSError as e:
            if e.errno == 48:  # Address already in use
                error_msg = (
                    f"Port {self.feedback_port} already in use. Is another instance running?"
                )
            else:
                error_msg = f"Failed to start feedback server: {e}"
            logger.error(error_msg)
            raise OSError(error_msg) from e

    async def disconnect(self) -> None:
        """
        Disconnect from Ardour.

        Cleanly shuts down the OSC client and feedback server.
        """
        with self._lock:
            if not self._connected:
                logger.warning("Not connected to Ardour")
                return

            logger.info("Disconnecting from Ardour...")

            # Shutdown feedback server
            if self.server:
                try:
                    self.server.shutdown()
                    logger.debug("Feedback server shutdown complete")
                except Exception as e:
                    logger.error(f"Error shutting down feedback server: {e}")

            # Wait for server thread to finish
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2.0)
                if self.server_thread.is_alive():
                    logger.warning("Feedback server thread did not terminate cleanly")

            # Clear client
            self.client = None
            self.server = None
            self.server_thread = None

            self._connected = False
            logger.info("Disconnected from Ardour")

    def send_command(self, address: str, *args: Any) -> bool:
        """
        Send an OSC command to Ardour.

        Args:
            address: OSC address pattern (e.g., "/transport_play")
            *args: Arguments for the OSC message

        Returns:
            True if command sent successfully, False otherwise
        """
        if not self._connected or self.client is None:
            logger.error(f"Cannot send command {address}: not connected")
            return False

        try:
            # Convert args to list for python-osc
            osc_args = list(args) if args else []
            self.client.send_message(address, osc_args)
            logger.debug(f"Sent OSC command: {address} {osc_args}")
            return True

        except Exception as e:
            logger.error(f"Failed to send OSC command {address}: {e}", exc_info=True)
            return False

    def register_feedback_handler(
        self, address: str, handler: Callable[[str, List[Any]], None]
    ) -> None:
        """
        Register a handler for OSC feedback messages.

        Handlers are called when feedback messages matching the address
        pattern are received from Ardour.

        Args:
            address: OSC address pattern to handle (e.g., "/transport_frame")
            handler: Callback function(address, args)
        """
        # Store handler for potential removal
        if address not in self.feedback_handlers:
            self.feedback_handlers[address] = []
        self.feedback_handlers[address].append(handler)

        # Create wrapper that extracts args from OscMessage
        def wrapper(unused_addr: str, *args: Any) -> None:
            try:
                handler(address, list(args))
            except Exception as e:
                logger.error(f"Error in feedback handler for {address}: {e}", exc_info=True)

        # Register with dispatcher
        self.dispatcher.map(address, wrapper)
        logger.debug(f"Registered feedback handler for: {address}")

    def unregister_feedback_handler(self, address: str) -> None:
        """
        Unregister all handlers for an address pattern.

        Args:
            address: OSC address pattern to unregister
        """
        if address in self.feedback_handlers:
            del self.feedback_handlers[address]
            # Note: python-osc dispatcher doesn't support unmap,
            # so handlers remain but won't be in our tracking dict
            logger.debug(f"Unregistered feedback handlers for: {address}")

    def _default_feedback_handler(self, address: str, *args: Any) -> None:
        """
        Default handler for unregistered feedback messages.

        Logs received messages for debugging purposes.

        Args:
            address: OSC address that was received
            *args: Arguments in the OSC message
        """
        logger.debug(f"Received unhandled OSC feedback: {address} {args}")

    def is_connected(self) -> bool:
        """
        Check if connected to Ardour.

        Returns:
            True if connected, False otherwise
        """
        with self._lock:
            return self._connected

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information.

        Returns:
            Dictionary with connection details
        """
        return {
            "connected": self._connected,
            "ardour_host": self.ardour_host,
            "ardour_port": self.ardour_port,
            "feedback_port": self.feedback_port,
            "handlers_registered": len(self.feedback_handlers),
        }
