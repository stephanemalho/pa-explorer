from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.models import cube  # noqa: F401 — enregistre Cube dans la metadata SQLAlchemy
from app.models import dimension  # noqa: F401 — enregistre Dimension dans la metadata SQLAlchemy
from app.routers import health, servers, cubes, dimensions


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(servers.router, prefix="/api/v1")
app.include_router(cubes.router, prefix="/api/v1")
app.include_router(dimensions.router, prefix="/api/v1")
