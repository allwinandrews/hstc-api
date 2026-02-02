"""FastAPI app entrypoint and route registration."""

from fastapi import FastAPI

from app.api.routes.gates import router as gates_router
from app.api.routes.transport import router as transport_router

app = FastAPI(
    title="Hyperspace Tunneling Corp API",
    version="0.1.0",
)

app.include_router(gates_router)
app.include_router(transport_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Lightweight liveness probe for deployment and tests."""
    return {"status": "ok"}
