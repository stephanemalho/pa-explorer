from fastapi import FastAPI

from app.config import settings
import app.models  # noqa: F401 — enregistre tous les modèles dans Base.metadata
from app.routers import health, servers, cubes, dimensions, auth


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(servers.router, prefix="/api/v1")
app.include_router(cubes.router, prefix="/api/v1")
app.include_router(dimensions.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
