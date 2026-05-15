from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.models import cube  # noqa: F401 — enregistre Cube dans la metadata SQLAlchemy
from app.models import dimension  # noqa: F401 — enregistre Dimension dans la metadata SQLAlchemy
from app.models import user  # noqa: F401 — enregistre User dans la metadata SQLAlchemy
from app.models import user_session  # noqa: F401 — enregistre UserSession dans la metadata SQLAlchemy
from app.models import user_allowlist  # noqa: F401 — enregistre UserAllowlist dans la metadata SQLAlchemy
from app.models import magic_link_token  # noqa: F401 — enregistre MagicLinkToken dans la metadata SQLAlchemy
from app.routers import health, servers, cubes, dimensions, auth


def _seed_allowlist() -> None:
    from app.database import SessionLocal
    from app.models.user_allowlist import UserAllowlist
    db = SessionLocal()
    try:
        email = settings.pa_explorer_initial_admin_email
        exists = db.query(UserAllowlist).filter(UserAllowlist.email == email).first()
        if not exists:
            db.add(UserAllowlist(email=email))
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_allowlist()
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
app.include_router(auth.router, prefix="/api/v1")
