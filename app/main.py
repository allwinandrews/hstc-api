from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.gates import router as gates_router
from app.api.routes.transport import router as transport_router
from app.db.init_db import init_db

app = FastAPI(title=settings.app_name)

# Routers
app.include_router(gates_router)
app.include_router(transport_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Render health check is configured as /healthz
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    """
    Ensure tables + seed exist on startup.

    This prevents 500s like:
    - relation "gates" does not exist
    when the Render Postgres instance is empty/new.
    """
    await init_db()
