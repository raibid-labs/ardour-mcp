"""
Session information MCP tools.

Provides tools for querying session information:
- Session details (name, sample rate, tempo)
- Marker lists
- Session statistics
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


# TODO: Implement session information tools
# These will be implemented in Phase 1, Issue #4


async def get_session_info() -> Dict[str, Any]:
    """
    Get current session information.

    Returns:
        Dictionary with session details (name, sample rate, tempo, etc.)
    """
    # TODO: Implement
    logger.info("get_session_info() - Not yet implemented")
    return {"success": False, "error": "Not yet implemented"}


async def list_markers() -> Dict[str, Any]:
    """
    List all markers in the session.

    Returns:
        Dictionary with list of markers
    """
    # TODO: Implement
    logger.info("list_markers() - Not yet implemented")
    return {"success": False, "error": "Not yet implemented"}


async def get_tempo() -> Dict[str, Any]:
    """
    Get current session tempo.

    Returns:
        Dictionary with tempo (BPM)
    """
    # TODO: Implement
    logger.info("get_tempo() - Not yet implemented")
    return {"success": False, "error": "Not yet implemented"}


async def get_time_signature() -> Dict[str, Any]:
    """
    Get current time signature.

    Returns:
        Dictionary with time signature (e.g., 4/4)
    """
    # TODO: Implement
    logger.info("get_time_signature() - Not yet implemented")
    return {"success": False, "error": "Not yet implemented"}
