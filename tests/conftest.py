"""Shared pytest fixtures for API and async event loop setup."""

import sys
import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.session import engine


# Fix asyncpg + ProactorEventLoop issues on Windows during pytest teardown
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Ensure pytest-asyncio uses a single stable event loop for the whole test session
@pytest.fixture(scope="session")
def event_loop():
    """Provide a single event loop for the full test session."""
    loop = asyncio.new_event_loop()
    yield loop

    # Dispose DB connections BEFORE closing loop
    # (if dispose fixture below didn't run for some reason)
    if not loop.is_closed():
        loop.run_until_complete(engine.dispose())

    loop.close()


@pytest.fixture(scope="session")
def base_url() -> str:
    """Stable base URL used by the AsyncClient."""
    return "http://test"


@pytest_asyncio.fixture
async def client(base_url: str):
    """Async HTTP client wired to the FastAPI app for integration tests."""
    # Explicitly run FastAPI startup/shutdown so background tasks don't leak
    await app.router.startup()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        yield ac

    # Close DB pool cleanly, then shutdown app
    await engine.dispose()
    await app.router.shutdown()
