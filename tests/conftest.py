"""Test configuration and fixtures."""

import pytest
import sys
import os

# Add src to Python path for tests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    from cli_server.server import get_server
except ModuleNotFoundError:  # pragma: no cover - environment guard
    get_server = None
    pytestmark = pytest.mark.skip(reason="cli_server package is not available in this environment")


@pytest.fixture
def cli_server():
    """Get the CLI server instance for testing."""
    if get_server is None:
        pytest.skip("cli_server package is not available")
    return get_server()