"""
Pytest configuration and fixtures for testing.

Provides common fixtures for database testing and other shared test utilities.
"""

import asyncio
import os
from pathlib import Path
import pytest
from sqlalchemy import text


def pytest_configure(config):
    """
    Pytest hook that runs before test collection.

    This is the earliest point we can modify the environment.
    We load .env.test here to ensure it's available before any
    app modules are imported.
    """
    from dotenv import load_dotenv

    test_env_path = Path(__file__).parent.parent / ".env.test"
    if test_env_path.exists():
        load_dotenv(test_env_path, override=True)
        print(f"Loaded test environment from {test_env_path}")


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio backend for async tests."""
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
