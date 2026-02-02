from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine

# Import models here so Base.metadata is populated before create_all()
from app.models.gate import Gate
from app.models.route import Route


async def _seed_data(session: AsyncSession) -> None:
    """
    Seed initial gates/routes if the database is empty.

    This must be idempotent (safe to run multiple times).
    We only seed when there are zero gates.
    """
    gate_count = await session.scalar(select(func.count()).select_from(Gate))
    if gate_count and gate_count > 0:
        return

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

    # Routes are one-way edges. Distances are HU and are direction-sensitive.
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


async def init_db() -> None:
    """
    Ensure schema exists, then seed required reference data.

    Render Free tier can't run a pre-deploy command, so the safest approach is
    to initialize on app startup.

    IMPORTANT:
    - Must be idempotent (seed only if empty)
    - Should not run during tests (tests bring their own DB setup/overrides)
    """
    if settings.environment.lower() == "test":
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await _seed_data(session)
