"""
Ardour MCP - Model Context Protocol server for Ardour DAW

This package provides MCP tools for controlling Ardour through AI assistants.
"""

__version__ = "0.0.1"
__author__ = "Raibid Labs"
__license__ = "MIT"

from ardour_mcp.server import main

__all__ = ["main", "__version__"]
