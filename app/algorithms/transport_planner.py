"""Transport cost model and decision logic for personal vs HSTC travel."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class TripCost:
    """Per-trip pricing and capacity for a single transport mode."""
    per_trip_gbp: float
    capacity: int


@dataclass(frozen=True)
class TransportPlan:
    """Computed cheapest plan plus the full cost breakdown."""
    distance_au: float
    passengers: int
    parking_days: int

    # hstc_trips = number of HSTC trips required.
    # personal_trips = number of personal vehicles required (each vehicle makes one journey).
    hstc_trips: int
    personal_trips: int

    # hstc_trip_cost_gbp is travel cost for ONE HSTC trip.
    # personal_trip_cost_gbp is total cost for ONE personal vehicle:
    # travel (0.30 * distance) + parking (5 * parking_days).
    hstc_trip_cost_gbp: float
    personal_trip_cost_gbp: float

    total_capacity: int
    total_cost_gbp: float

    hstc_total_gbp: float
    personal_total_gbp: float


def _round_money(value: float) -> float:
    """Round to two decimal places using standard currency rounding."""
    return round(float(value), 2)


def compute_transport_plan(distance_au: float, passengers: int, parking_days: int) -> TransportPlan:
    """
    Compute the cheapest transport plan to reach the nearest gate (distance in AU).

    Business rules enforced here:
    - Choose exactly one mode: personal-only OR HSTC-only (no mixing).
    - Personal pricing:
        - Each vehicle carries up to 4 passengers.
        - Travel: 0.30 GBP per AU per vehicle.
        - Parking: 5 GBP per day per vehicle (scales with vehicle count).
    - HSTC pricing:
        - Each trip carries up to 5 passengers.
        - Travel: 0.45 GBP per AU per trip.
        - No parking cost.
    - Rounding: totals and per-trip costs are rounded to 2dp at the end
      so comparisons are based on rounded currency values.
    - Tie-breakers:
        1) fewer total movements (vehicles/trips)
        2) prefer HSTC (avoids parking complexity)

    Args:
        distance_au: Real-space distance to travel, in AU.
        passengers: Passenger count to move.
        parking_days: Days of parking required for personal vehicles.

    Returns:
        TransportPlan with the chosen mode, totals, and capacities.

    Raises:
        ValueError: If any input is non-positive (distance, passengers) or
            parking_days is negative.
    """
    if distance_au <= 0:
        raise ValueError("distance_au must be > 0")
    if passengers <= 0:
        raise ValueError("passengers must be > 0")
    if parking_days < 0:
        raise ValueError("parking_days must be >= 0")

    distance_au = float(distance_au)
    passengers = int(passengers)
    parking_days = int(parking_days)

    # Personal transport capacity and costs are computed per vehicle.
    personal_vehicles = math.ceil(passengers / 4)

    personal_travel_per_vehicle = 0.30 * distance_au
    personal_parking_per_vehicle = 5.0 * parking_days
    personal_per_vehicle_total = (
        personal_travel_per_vehicle + personal_parking_per_vehicle
    )

    personal_total = personal_vehicles * personal_per_vehicle_total
    personal_capacity = personal_vehicles * 4

    # HSTC trips are per 5-passenger capacity and do not include parking.
    hstc_trips = math.ceil(passengers / 5)

    hstc_per_trip = 0.45 * distance_au
    hstc_total = hstc_trips * hstc_per_trip
    hstc_capacity = hstc_trips * 5

    # Round only at the end to avoid rounding artifacts affecting comparisons.
    personal_total_r = _round_money(personal_total)
    hstc_total_r = _round_money(hstc_total)

    personal_per_vehicle_r = _round_money(personal_per_vehicle_total)
    hstc_per_trip_r = _round_money(hstc_per_trip)

    # Choose cheaper option first, then apply tie-breakers on equal totals.
    if personal_total_r < hstc_total_r:
        return TransportPlan(
            distance_au=distance_au,
            passengers=passengers,
            parking_days=parking_days,
            hstc_trips=0,
            personal_trips=personal_vehicles,  # vehicles
            hstc_trip_cost_gbp=hstc_per_trip_r,
            # per vehicle (travel + parking)
            personal_trip_cost_gbp=personal_per_vehicle_r,
            total_capacity=personal_capacity,
            total_cost_gbp=personal_total_r,
            hstc_total_gbp=_round_money(0.0),
            personal_total_gbp=personal_total_r,
        )

    if hstc_total_r < personal_total_r:
        return TransportPlan(
            distance_au=distance_au,
            passengers=passengers,
            parking_days=parking_days,
            hstc_trips=hstc_trips,
            personal_trips=0,
            hstc_trip_cost_gbp=hstc_per_trip_r,
            personal_trip_cost_gbp=personal_per_vehicle_r,
            total_capacity=hstc_capacity,
            total_cost_gbp=hstc_total_r,
            hstc_total_gbp=hstc_total_r,
            personal_total_gbp=_round_money(0.0),
        )

    # Tie: apply tie-breakers
    if hstc_trips <= personal_vehicles:
        return TransportPlan(
            distance_au=distance_au,
            passengers=passengers,
            parking_days=parking_days,
            hstc_trips=hstc_trips,
            personal_trips=0,
            hstc_trip_cost_gbp=hstc_per_trip_r,
            personal_trip_cost_gbp=personal_per_vehicle_r,
            total_capacity=hstc_capacity,
            total_cost_gbp=hstc_total_r,
            hstc_total_gbp=hstc_total_r,
            personal_total_gbp=_round_money(0.0),
        )

    return TransportPlan(
        distance_au=distance_au,
        passengers=passengers,
        parking_days=parking_days,
        hstc_trips=0,
        personal_trips=personal_vehicles,
        hstc_trip_cost_gbp=hstc_per_trip_r,
        personal_trip_cost_gbp=personal_per_vehicle_r,
        total_capacity=personal_capacity,
        total_cost_gbp=personal_total_r,
        hstc_total_gbp=_round_money(0.0),
        personal_total_gbp=personal_total_r,
    )
