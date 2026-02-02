"""Transport pricing endpoint with business-rule validation."""

import math
from fastapi import APIRouter, HTTPException, Query

from app.algorithms.transport_planner import compute_transport_plan
from app.api.schemas import TransportBreakdownOut, TransportResponseOut

router = APIRouter(prefix="/transport", tags=["transport"])


def _round_money(value: float) -> float:
    """Round to two decimal places to match the planner output."""
    return round(float(value), 2)


@router.get("/{distance}", response_model=TransportResponseOut)
async def get_transport_cost(
    distance: float,
    passengers: int = Query(..., gt=0),
    parking: int = Query(0, ge=0),
):
    """
    Compute transport pricing for a distance and passenger count.

    Validation rules:
    - distance must be > 0 (path parameter)
    - passengers must be > 0 (query parameter)
    - parking must be >= 0 (query parameter)

    Error responses:
    - 400 for invalid distance or planner validation errors
    - 422 for FastAPI query validation failures
    """
    if distance <= 0:
        raise HTTPException(status_code=400, detail="distance must be > 0")

    try:
        plan = compute_transport_plan(
            distance_au=distance, passengers=passengers, parking_days=parking
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Compute "pure" option totals for transparency.
    # HSTC-only: each trip carries up to 5.
    hstc_only_trips = math.ceil(passengers / 5)
    hstc_only_total = _round_money(hstc_only_trips * (0.45 * distance))

    # Personal-only: each vehicle carries up to 4 and pays parking.
    personal_only_vehicles = math.ceil(passengers / 4)
    personal_trip_with_parking = (
        0.30 * distance) + (5.0 * parking)  # per vehicle
    personal_only_total = _round_money(
        personal_only_vehicles * personal_trip_with_parking)

    # Label the chosen plan for the response schema.
    if plan.hstc_trips > 0 and plan.personal_trips > 0:
        chosen_mode = "MIXED"
    elif plan.hstc_trips > 0:
        chosen_mode = "HSTC"
    else:
        chosen_mode = "PERSONAL"

    return TransportResponseOut(
        distance_au=plan.distance_au,
        passengers=plan.passengers,
        parking_days=plan.parking_days,
        total_cost_gbp=plan.total_cost_gbp,
        plan=TransportBreakdownOut(
            hstc_trips=plan.hstc_trips,
            personal_trips=plan.personal_trips,
            hstc_trip_cost_gbp=plan.hstc_trip_cost_gbp,
            personal_trip_cost_gbp=plan.personal_trip_cost_gbp,
            hstc_total_gbp=plan.hstc_total_gbp,
            personal_total_gbp=plan.personal_total_gbp,
            total_capacity=plan.total_capacity,
        ),
        # Additional response fields for transparency.
        hstc_only_total_gbp=hstc_only_total,
        personal_only_total_gbp=personal_only_total,
        chosen_mode=chosen_mode,
    )
