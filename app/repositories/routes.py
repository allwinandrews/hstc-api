"""Repository for route lookups used by routing algorithms."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route


class RouteRepository:
    """Database access for route records."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all_routes(self) -> list[Route]:
        """Return all routes as directed edges for graph algorithms."""
        # For our small graph, loading all edges is simplest and fastest.
        # If the graph grows, we can optimize to adjacency queries per node.
        result = await self.session.execute(select(Route))
        return list(result.scalars().all())
