"""
Ardour MCP - Model Context Protocol server for Ardour DAW

This package provides MCP tools for controlling Ardour through AI assistants.
"""

try:
    from ardour_mcp._version import __version__
except ImportError:
    # Fallback for development without a git tag
    __version__ = "0.0.0.dev0"

__author__ = "Raibid Labs"
__license__ = "MIT"

from ardour_mcp.server import main

__all__ = ["main", "__version__"]
