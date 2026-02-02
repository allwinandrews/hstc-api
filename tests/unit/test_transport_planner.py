"""Unit tests for transport pricing and tie-breakers."""

import pytest

from app.algorithms.transport_planner import compute_transport_plan


def test_transport_invalid_inputs():
    """Rejects non-positive distance/passengers and negative parking."""
    with pytest.raises(ValueError):
        compute_transport_plan(distance_au=0, passengers=1, parking_days=0)

    with pytest.raises(ValueError):
        compute_transport_plan(distance_au=1, passengers=0, parking_days=0)

    with pytest.raises(ValueError):
        compute_transport_plan(distance_au=1, passengers=1, parking_days=-1)


def test_transport_boundary_capacities_parking_zero():
    """Checks capacity math and cost comparisons with zero parking."""
    # Distance=1, parking=0
    # Personal trip: 0.30, cap 4
    # HSTC trip: 0.45, cap 5

    # 4 pax -> 1 personal is cheapest
    plan = compute_transport_plan(distance_au=1, passengers=4, parking_days=0)
    assert plan.personal_trips == 1
    assert plan.hstc_trips == 0
    assert plan.total_cost_gbp == 0.30

    # 5 pax -> 1 HSTC is cheapest (1 personal can't carry 5)
    plan = compute_transport_plan(distance_au=1, passengers=5, parking_days=0)
    assert plan.hstc_trips == 1
    assert plan.personal_trips == 0
    assert plan.total_cost_gbp == 0.45

    # 6 pax -> 2 personal trips cost 0.60 vs 2 HSTC trips cost 0.90 -> personal wins
    plan = compute_transport_plan(distance_au=1, passengers=6, parking_days=0)
    assert plan.personal_trips == 2
    assert plan.hstc_trips == 0
    assert plan.total_cost_gbp == 0.60


def test_transport_parking_makes_hstc_preferred():
    """Parking costs should tip the decision toward HSTC at small distances."""
    # With parking, personal becomes expensive quickly.
    # distance=1, parking=2: personal trip = 0.30 + 10 = 10.30
    # hstc trip = 0.45
    plan = compute_transport_plan(distance_au=1, passengers=7, parking_days=2)
    assert plan.hstc_trips == 2
    assert plan.personal_trips == 0
    assert plan.total_cost_gbp == 0.90


def test_transport_decimal_distance_rounding():
    """Ensures currency rounding occurs after totals are computed."""
    # distance=1.5, parking=0
    # personal per trip: 0.45
    # hstc per trip: 0.675 -> 0.68 after rounding
    plan = compute_transport_plan(
        distance_au=1.5, passengers=4, parking_days=0)
    assert plan.personal_trips == 1
    assert plan.total_cost_gbp == 0.45

    plan = compute_transport_plan(
        distance_au=1.5, passengers=5, parking_days=0)
    assert plan.hstc_trips == 1
    assert plan.total_cost_gbp == 0.68
