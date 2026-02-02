"""Pydantic response schemas for API endpoints."""

from pydantic import BaseModel, Field


class RouteOut(BaseModel):
    """Outgoing directed route from a gate."""
    to_code: str = Field(..., min_length=3, max_length=3)
    hu_distance: int = Field(..., gt=0)


class GateOut(BaseModel):
    """Basic gate summary used in list views."""
    code: str = Field(..., min_length=3, max_length=3)
    name: str


class GateDetailOut(GateOut):
    """Gate details including outgoing routes."""
    outgoing: list[RouteOut]


class CheapestPathOut(BaseModel):
    """Shortest path response; includes optional hyperspace cost."""
    path: list[str] = Field(..., min_length=2)
    total_hu: int = Field(..., gt=0)
    passengers: int | None = Field(default=None, gt=0)
    hyperspace_cost_gbp: float | None = Field(default=None, ge=0)


class TransportBreakdownOut(BaseModel):
    """Breakdown of trips, per-trip costs, and totals for a single-mode plan."""
    hstc_trips: int = Field(..., ge=0)
    personal_trips: int = Field(..., ge=0)

    hstc_trip_cost_gbp: float = Field(..., ge=0)
    personal_trip_cost_gbp: float = Field(..., ge=0)

    hstc_total_gbp: float = Field(..., ge=0)
    personal_total_gbp: float = Field(..., ge=0)

    total_capacity: int = Field(..., ge=0)


class TransportResponseOut(BaseModel):
    """Transport pricing response including the chosen single-mode plan and both mode totals."""
    distance_au: float = Field(..., gt=0)
    passengers: int = Field(..., gt=0)
    parking_days: int = Field(..., ge=0)

    # Cheapest single-mode plan chosen by the transport planner.
    total_cost_gbp: float = Field(..., ge=0)
    plan: TransportBreakdownOut

    # Expose pure-mode totals for transparency in client UIs.
    hstc_only_total_gbp: float = Field(..., ge=0)
    personal_only_total_gbp: float = Field(..., ge=0)

    # Chosen mode is always "HSTC" or "PERSONAL" for single-mode plans.
    chosen_mode: str = Field(..., min_length=1)
