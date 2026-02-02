"""Shared pytest fixtures for API, async event loop, and test DB setup."""

import os
os.environ.setdefault("ENVIRONMENT", "test")

from app.models.route import Route
from app.models.gate import Gate
from app.db.session import get_db_session
from app.db.base import Base
from app.main import app
import sys
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


# Import models so Base.metadata is populated


# Fix Windows event loop edge-cases during pytest teardown.
# This helps avoid "Event loop is closed" / Proactor transport issues on Windows.
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def event_loop():
    """Provide a single event loop for the full test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def base_url() -> str:
    """Stable base URL used by the AsyncClient."""
    return "http://test"


@pytest.fixture(scope="session")
def test_engine():
    """
    Test database engine.

    Uses SQLite so CI doesn't need a running Postgres instance.
    File-based SQLite is more stable than in-memory for async tests.
    """
    return create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        future=True,
    )


@pytest.fixture(scope="session")
def TestSessionLocal(test_engine):
    """Async session factory bound to the test DB engine."""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db(test_engine, TestSessionLocal):
    """
    Create tables + seed data once for the test session.

    Important:
    - Seeding must use an ORM Session (AsyncSession), not an engine Connection.
      Connections do not support ORM methods like add_all().
    """
    async with test_engine.begin() as conn:
        # Recreate schema fresh each test run
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Seed data using an AsyncSession (ORM)
    async with TestSessionLocal() as session:
        gates = [
            Gate(code="SOL", name="Sol"),
            Gate(code="PRX", name="Proxima"),
            Gate(code="SIR", name="Sirius"),
            Gate(code="CAS", name="Castor"),
            Gate(code="PRO", name="Procyon"),
            Gate(code="DEN", name="Denebula"),
            Gate(code="RAN", name="Ran"),
            Gate(code="ARC", name="Arcturus"),
            Gate(code="FOM", name="Fomalhaut"),
            Gate(code="ALT", name="Altair"),
            Gate(code="VEG", name="Vega"),
            Gate(code="ALD", name="Aldermain"),
            Gate(code="ALS", name="Alshain"),
        ]
        session.add_all(gates)

        routes = [
            Route(from_code="SOL", to_code="RAN", hu_distance=100),
            Route(from_code="SOL", to_code="PRX", hu_distance=90),
            Route(from_code="SOL", to_code="SIR", hu_distance=100),
            Route(from_code="SOL", to_code="ARC", hu_distance=200),
            Route(from_code="SOL", to_code="ALD", hu_distance=250),

            Route(from_code="PRX", to_code="SOL", hu_distance=90),
            Route(from_code="PRX", to_code="SIR", hu_distance=100),
            Route(from_code="PRX", to_code="ALT", hu_distance=150),

            Route(from_code="SIR", to_code="SOL", hu_distance=80),
            Route(from_code="SIR", to_code="PRX", hu_distance=10),
            Route(from_code="SIR", to_code="CAS", hu_distance=200),

            Route(from_code="CAS", to_code="SIR", hu_distance=200),
            Route(from_code="CAS", to_code="PRO", hu_distance=120),

            Route(from_code="PRO", to_code="CAS", hu_distance=80),

            Route(from_code="DEN", to_code="PRO", hu_distance=5),
            Route(from_code="DEN", to_code="ARC", hu_distance=2),
            Route(from_code="DEN", to_code="FOM", hu_distance=8),
            Route(from_code="DEN", to_code="RAN", hu_distance=100),
            Route(from_code="DEN", to_code="ALD", hu_distance=3),

            Route(from_code="RAN", to_code="SOL", hu_distance=100),

            Route(from_code="ARC", to_code="SOL", hu_distance=500),
            Route(from_code="ARC", to_code="DEN", hu_distance=120),

            Route(from_code="FOM", to_code="PRX", hu_distance=10),
            Route(from_code="FOM", to_code="DEN", hu_distance=20),
            Route(from_code="FOM", to_code="ALS", hu_distance=9),

            Route(from_code="ALT", to_code="FOM", hu_distance=140),
            Route(from_code="ALT", to_code="VEG", hu_distance=220),

            Route(from_code="VEG", to_code="ARC", hu_distance=220),
            Route(from_code="VEG", to_code="ALD", hu_distance=580),

            Route(from_code="ALD", to_code="SOL", hu_distance=200),
            Route(from_code="ALD", to_code="ALS", hu_distance=160),
            Route(from_code="ALD", to_code="VEG", hu_distance=320),

            Route(from_code="ALS", to_code="ALT", hu_distance=1),
            Route(from_code="ALS", to_code="ALD", hu_distance=1),
        ]
        session.add_all(routes)

        await session.commit()

    yield

    # Dispose engine after tests
    await test_engine.dispose()


@pytest_asyncio.fixture
async def client(base_url: str, TestSessionLocal) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client wired to the FastAPI app for integration tests.

    Overrides the DB dependency so tests run against SQLite and don't require Postgres.
    """

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            yield session

    # Override BEFORE startup so anything during startup uses the test session.
    app.dependency_overrides[get_db_session] = override_get_db_session

    await app.router.startup()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        yield ac

    await app.router.shutdown()
    app.dependency_overrides.clear()
