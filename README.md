# Technical Challenge - Interstellar Route Planner

## Brief

Hyperspace Tunneling Corp manages a system-to-system web of hyperspace gates. They charge a fee to their users and now also transport people to and through the gate network. The goal is to calculate journey costs for clients.

A journey is defined as:

- Journey to the gate (real space)
- Outbound and inbound hyperspace journeys between gates

Transport to the gate:

- Personal transport: 0.30 GBP per AU plus 5 GBP per day for ship storage at the gate (fits up to 4 people)
- HSTC transport: 0.45 GBP per AU (fits up to 5 people)

Hyperspace journey::

- Spaceflight: 0.10 GBP per passenger per hyperplane unit (HU)
- Total hyperspace cost is outbound + inbound (2x the one-way cost)

Units:

- AU (Astronomical Unit) is roughly 149,597,870.7 km
- HU (Hyperplane Unit) is a fictional unit for gate-to-gate distance

Gates are typically one-way; A->B does not imply B->A, and HU distance can differ by direction.

Gate data (directed edges and HU distances) is seeded locally via SQL.

## API Requirements

The API should expose at least the following public endpoints:

- GET /transport/{distance}?passengers={number}&parking={days}
  - Returns the cheapest vehicle to use (and the cost) for the given distance (in AU), passenger count, and parking days.
- GET /gates
  - Returns a list of gates with their information.
- GET /gates/{gateCode}
  - Returns the details of a single gate.
- GET /gates/{gateCode}/to/{targetGateCode}
  - Returns the cheapest route from gateCode to targetGateCode.

## Local Development

Prerequisites:

- Python 3.11+
- Docker (for local Postgres)

1. Create and activate a virtual environment, then install dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start Postgres (seeds gate and route data on first run).

```powershell
docker compose up -d
```

3. Run the API.

```powershell
uvicorn app.main:app --reload
```

The OpenAPI docs are available at:
`http://localhost:8000/docs`

## Deployment

The API (and its interactive docs) is deployed on Render at `https://hstc-api.onrender.com/docs`.

## Environment

Configuration defaults are defined in `app/core/config.py`. Override via `.env`.

## Tests

```powershell
pytest
```
