"""Repository for gate lookups and related routes."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gate import Gate
from app.models.route import Route


class GateRepository:
    """Database access for gate records and outgoing routes."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_gates(self) -> list[Gate]:
        """Return all gates ordered by code for stable API output."""
        result = await self.session.execute(select(Gate).order_by(Gate.code))
        return list(result.scalars().all())

    async def get_gate(self, code: str) -> Gate | None:
        """Return a gate by 3-letter code, or None if not found."""
        result = await self.session.execute(select(Gate).where(Gate.code == code))
        return result.scalars().first()

    async def list_outgoing_routes(self, from_code: str) -> list[Route]:
        """Return all directed routes that depart from the given gate."""
        result = await self.session.execute(
            select(Route).where(Route.from_code ==
                                from_code).order_by(Route.to_code)
        )
        return list(result.scalars().all())
