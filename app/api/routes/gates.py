"""Gate and routing endpoints, including cheapest-path calculations."""

from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms.dijkstra import dijkstra_shortest_path
from app.api.schemas import CheapestPathOut, GateDetailOut, GateOut, RouteOut
from app.db.session import get_db_session
from app.repositories.gates import GateRepository
from app.repositories.routes import RouteRepository

router = APIRouter(prefix="/gates", tags=["gates"])


@router.get("", response_model=list[GateOut])
async def list_gates(session: AsyncSession = Depends(get_db_session)):
    """Return all gates ordered by code."""
    repo = GateRepository(session)
    gates = await repo.list_gates()
    return [GateOut(code=g.code, name=g.name) for g in gates]


@router.get("/{gate_code}", response_model=GateDetailOut)
async def get_gate(gate_code: str, session: AsyncSession = Depends(get_db_session)):
    """Return a single gate with its outgoing directed routes."""
    if len(gate_code) != 3:
        raise HTTPException(
            status_code=400, detail="gateCode must be a 3-letter code")

    repo = GateRepository(session)
    gate = await repo.get_gate(gate_code)
    if gate is None:
        raise HTTPException(
            status_code=404, detail=f"Gate '{gate_code}' not found")

    routes = await repo.list_outgoing_routes(gate_code)

    return GateDetailOut(
        code=gate.code,
        name=gate.name,
        outgoing=[RouteOut(to_code=r.to_code, hu_distance=r.hu_distance)
                  for r in routes],
    )


@router.get("/{gate_code}/to/{target_gate_code}", response_model=CheapestPathOut)
async def get_cheapest_path(
    gate_code: str,
    target_gate_code: str,
    passengers: int | None = Query(default=None, gt=0),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Return the cheapest directed path and optional hyperspace cost.

    Validation rules:
    - gate codes must be exactly 3 characters
    - passengers (if provided) must be > 0

    Error responses:
    - 400 for invalid gate codes
    - 404 if either gate is missing or no route exists
    """
    # Basic validation (we keep it simple: codes must be 3 letters)
    if len(gate_code) != 3 or len(target_gate_code) != 3:
        raise HTTPException(
            status_code=400, detail="gate codes must be 3-letter codes")

    gate_repo = GateRepository(session)

    start_gate = await gate_repo.get_gate(gate_code)
    if start_gate is None:
        raise HTTPException(
            status_code=404, detail=f"Gate '{gate_code}' not found")

    end_gate = await gate_repo.get_gate(target_gate_code)
    if end_gate is None:
        raise HTTPException(
            status_code=404, detail=f"Gate '{target_gate_code}' not found")

    route_repo = RouteRepository(session)
    routes = await route_repo.list_all_routes()

    # Directed edges: each (from -> to) has its own HU weight.
    edges = [(r.from_code, r.to_code, r.hu_distance) for r in routes]
    result = dijkstra_shortest_path(edges, gate_code, target_gate_code)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No route from '{gate_code}' to '{target_gate_code}'",
        )

    # Hyperspace cost: one-way journey along the directed path.
    # total_cost = 0.10 * passengers * total_HU_of_path
    hyperspace_cost = None
    if passengers is not None:
        cost = (
            Decimal("0.10")
            * Decimal(passengers)
            * Decimal(result.total_weight)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        hyperspace_cost = float(cost)

    return CheapestPathOut(
        path=result.path,
        total_hu=result.total_weight,
        passengers=passengers,
        hyperspace_cost_gbp=hyperspace_cost,
    )
