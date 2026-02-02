# Task Status - Technical Challenge - Interstellar Route Planner

Source of requirements:
- `README.md` (challenge brief and expectations).

## Completed
- [x] Public API endpoint: transport cost to nearest gate.
  - Evidence: `app/api/routes/transport.py` (GET `/transport/{distance}`), `tests/integration/test_endpoints.py`.
  - Notes: Computes cheapest single-mode plan (personal vs HSTC) with parking and capacity rules; returns totals and breakdown.
- [x] Public API endpoint: list gates.
  - Evidence: `app/api/routes/gates.py` (GET `/gates`), `tests/integration/test_endpoints.py`.
  - Notes: Returns all gates with code and name.
- [x] Public API endpoint: gate details.
  - Evidence: `app/api/routes/gates.py` (GET `/gates/{gateCode}`), `tests/integration/test_endpoints.py`.
  - Notes: Returns gate plus outgoing directed routes.
- [x] Public API endpoint: cheapest route between gates.
  - Evidence: `app/api/routes/gates.py` (GET `/gates/{gateCode}/to/{targetGateCode}`), `app/algorithms/dijkstra.py`, `tests/integration/test_endpoints.py`.
  - Notes: Uses Dijkstra over directed edges; supports optional passenger cost.
- [x] Directed gate graph with asymmetric weights.
  - Evidence: `docker/postgres/01-init.sql`, `app/models/route.py`.
  - Notes: Routes are stored as directed edges; no reverse edge implied.
- [x] Hyperspace cost rule for outbound + inbound.
  - Evidence: `app/api/routes/gates.py`.
  - Notes: Cost is `2 * (0.10 * passengers * total_hu)` when passengers are provided.
- [x] Seed data for gates and routes.
  - Evidence: `docker/postgres/01-init.sql`, `docker-compose.yml`.
  - Notes: Postgres init script seeds gates and routes on container startup.
- [x] Tests.
  - Evidence: `tests/unit/test_dijkstra.py`, `tests/unit/test_transport_planner.py`, `tests/integration/test_endpoints.py`.
  - Notes: Unit tests cover routing and transport rules; integration tests cover public endpoints.
- [x] Application code in repository.
  - Evidence: `app/*`.
- [x] Challenge requirements documented.
  - Evidence: `README.md`.
  - Notes: Challenge brief and expectations are captured verbatim.
- [x] Local run instructions.
  - Evidence: `README.md`.
  - Notes: Includes venv setup, Docker Postgres, and `uvicorn` run steps.
- [x] API documentation artifact.
  - Evidence: `docs/openapi.json`.
  - Notes: Exported FastAPI OpenAPI schema.
- [x] CI/CD configuration.
  - Evidence: `.github/workflows/tests.yml`.
  - Notes: Runs `pytest` on push and pull requests.

## Pending / Missing
- [x] Deployed API link.
  - Evidence: `README.md`.
  - Notes: Render deployment available at `https://hstc-api.onrender.com/docs`.
- [x] Diagrams, plans, or design notes.
  - Evidence: `docs/architecture.md`.
  - Notes: High-level architecture summary covering FastAPI, repos, algorithms, and Postgres seed flow.
 - [ ] Infrastructure config/code (Terraform, etc.).
   - What is missing: infra-as-code beyond local Docker.
   - Where to implement: `infra/` or `terraform/`.
   - Suggested next step: add Terraform or equivalent if deployment is expected; current deployment was configured manually via the Render dashboard.

## Quality / Delivery
- [x] Deployed API link: provided (README now notes Render docs).
- [x] API docs available at runtime (FastAPI automatic docs).
  - Evidence: `app/main.py` (FastAPI app), `app/api/routes/*`.
- [x] API docs artifact: present.
  - Evidence: `docs/openapi.json`.
- [x] Diagrams/plans/notes: present (architecture summary added).
  - Evidence: `docs/architecture.md`.
- [x] Tests: present (unit + integration).
  - Evidence: `tests/unit/*`, `tests/integration/test_endpoints.py`.
- [x] CI/CD config: present.
  - Evidence: `.github/workflows/tests.yml`.
- [ ] Infra config: partially present (local `docker-compose.yml` + Render notes only).
- [x] Local run instructions: present.
  - Evidence: `README.md`.
- [x] Supporting scripts: present.
  - Evidence: `docker/postgres/01-init.sql`, `docker-compose.yml`, `debug_asyncpg.py`.
