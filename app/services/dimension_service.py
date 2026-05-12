import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.clients.ibm_pa import IBMPAClient
from app.config import settings
from app.models.dimension import Dimension

logger = logging.getLogger(__name__)


class DimensionService:
    def __init__(self, db: Session, client: IBMPAClient) -> None:
        self._db = db
        self._client = client

    def get_dimensions(
        self, server_name: str, cube_name: str, force_refresh: bool = False
    ) -> tuple[list[Dimension], bool]:
        if not force_refresh:
            cached = self._get_cached_dimensions(server_name, cube_name)
            if cached is not None:
                logger.info(
                    "Serving %d dimension(s) from cache for cube %s/%s",
                    len(cached), server_name, cube_name,
                )
                return cached, True

        dimensions = self._refresh_from_ibm_pa(server_name, cube_name)
        return dimensions, False

    def _get_cached_dimensions(
        self, server_name: str, cube_name: str
    ) -> Optional[list[Dimension]]:
        dimensions = (
            self._db.query(Dimension)
            .filter(Dimension.server_name == server_name, Dimension.cube_name == cube_name)
            .all()
        )
        if not dimensions:
            return None
        expires = dimensions[0].cache_expires_at
        if not expires:
            return None
        now = datetime.now(timezone.utc)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires > now:
            return dimensions
        return None

    def _refresh_from_ibm_pa(self, server_name: str, cube_name: str) -> list[Dimension]:
        raw_dimensions = self._client.get_dimensions(server_name, cube_name)
        logger.info(
            "IBM PA returned %d dimension(s) for cube %s/%s",
            len(raw_dimensions), server_name, cube_name,
        )

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.ibm_pa_dimensions_ttl_seconds)
        now = datetime.now(timezone.utc)

        for raw in raw_dimensions:
            name = raw.get("Name") or raw.get("name", "")
            if not name:
                continue

            dimension = (
                self._db.query(Dimension)
                .filter(
                    Dimension.server_name == server_name,
                    Dimension.cube_name == cube_name,
                    Dimension.name == name,
                )
                .first()
            )
            if not dimension:
                dimension = Dimension(name=name, server_name=server_name, cube_name=cube_name)
                self._db.add(dimension)

            dimension.unique_name = raw.get("UniqueName")
            dimension.raw_data = json.dumps(raw)
            dimension.last_synced_at = now
            dimension.cache_expires_at = expires_at

        self._db.commit()
        return (
            self._db.query(Dimension)
            .filter(Dimension.server_name == server_name, Dimension.cube_name == cube_name)
            .all()
        )
