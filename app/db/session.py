"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Create a single async engine for the whole app.
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set True temporarily if you want verbose SQL logs.
    pool_pre_ping=True,
)

# Factory for async sessions (request-scoped usage).
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncSession:
    """FastAPI dependency that yields a request-scoped AsyncSession."""
    async with AsyncSessionLocal() as session:
        yield session
