# Architecture Notes

## High-level flow

```
Client request
     ↓
FastAPI (`app.main`)
     ↓
Router layer (`app.api.routes.*`)
     ↙                         ↘
Repository layer               Transport/algorithm layer
(SQLAlchemy, async Postgres)   (`app.algorithms.dijkstra`, `app.algorithms.transport_planner`)
     ↓
Postgres (seeded via `docker/postgres/01-init.sql` or `app.db.init_db`)
```

- **Gate endpoints** query `GateRepository`/`RouteRepository` for gate metadata and run Dijkstra to build directed paths before returning `CheapestPathOut`.
- **Transport endpoint** delegates to `compute_transport_plan`, which applies capacity limits, per-AU pricing, and optional parking fees for transparency.
- `init_db` runs every startup so new deployments (Render/Postgres) auto-create tables and seed gate/route data before the first request.

## Supporting pieces

- **Settings** (`app.core.config.Settings`) read `DATABASE_URL` first (Render) then the individual `DB_*` values for local Docker.
- **Database session** uses `app.db.session.get_db_session` to supply `AsyncSession` to repositories that translate ORM records into schema models.
- **Schemas** (`app.api.schemas`) define the OpenAPI contract that’s exposed at `/docs` (FastAPI auto docs).

Optional enhancements: add a sequence diagram later if reviewers want a visual path for routing + transport calculations.
