"""Integration tests for HTTP endpoints and response schemas."""

import pytest


@pytest.mark.asyncio
async def test_health(client):
    """Health endpoint returns a stable OK payload."""
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_gates(client):
    """Gate listing returns a non-empty list with known seed data."""
    r = await client.get("/gates")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 10
    assert {"code": "SOL", "name": "Sol"} in data


@pytest.mark.asyncio
async def test_get_gate_details(client):
    """Gate details include outgoing routes."""
    r = await client.get("/gates/SOL")
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == "SOL"
    assert body["name"] == "Sol"
    assert isinstance(body["outgoing"], list)
    assert any(x["to_code"] == "PRX" for x in body["outgoing"])


@pytest.mark.asyncio
async def test_get_gate_not_found(client):
    """Unknown gate code returns 404."""
    r = await client.get("/gates/XXX")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_cheapest_path_without_passengers(client):
    """Cheapest path works without optional passengers pricing."""
    r = await client.get("/gates/SOL/to/ALS")
    assert r.status_code == 200
    body = r.json()
    assert body["path"][0] == "SOL"
    assert body["path"][-1] == "ALS"
    assert body["total_hu"] > 0
    assert body["passengers"] is None
    assert body["hyperspace_cost_gbp"] is None


@pytest.mark.asyncio
async def test_cheapest_path_with_passengers(client):
    """Cheapest path includes hyperspace cost when passengers are provided."""
    r = await client.get("/gates/SOL/to/ALS?passengers=3")
    assert r.status_code == 200
    body = r.json()
    assert body["passengers"] == 3
    assert body["hyperspace_cost_gbp"] == 101.1


@pytest.mark.asyncio
async def test_cheapest_path_with_passengers_prx_to_cas(client):
    """Cheapest path pricing matches one-way hyperspace cost."""
    r = await client.get("/gates/PRX/to/CAS?passengers=2")
    assert r.status_code == 200
    body = r.json()
    assert body["passengers"] == 2
    assert body["hyperspace_cost_gbp"] == 60.0


@pytest.mark.asyncio
async def test_transport_endpoint(client):
    """Transport endpoint returns a structured plan with totals."""
    r = await client.get("/transport/1?passengers=7&parking=2")
    assert r.status_code == 200
    body = r.json()
    assert body["distance_au"] == 1
    assert body["passengers"] == 7
    assert body["parking_days"] == 2
    assert body["total_cost_gbp"] >= 0
    assert "plan" in body
    assert body["plan"]["hstc_trips"] >= 0
    assert body["plan"]["personal_trips"] >= 0


@pytest.mark.asyncio
async def test_transport_validation_errors(client):
    """Invalid transport inputs return proper HTTP status codes."""
    r = await client.get("/transport/0?passengers=1&parking=0")
    assert r.status_code == 400

    r = await client.get("/transport/1?passengers=0&parking=0")
    assert r.status_code == 422  # FastAPI query validation

    r = await client.get("/transport/1?passengers=1&parking=-1")
    assert r.status_code == 422  # FastAPI query validation
