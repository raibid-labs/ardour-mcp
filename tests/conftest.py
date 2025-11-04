"""
Pytest configuration and shared fixtures.
"""


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest asyncio."""
    config.option.asyncio_mode = "auto"
