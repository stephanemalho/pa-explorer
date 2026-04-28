import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.clients.ibm_pa import IBMPAClient
from app.config import settings
from app.models.server import Server

logger = logging.getLogger(__name__)


class ServerService:
    def __init__(self, db: Session, client: IBMPAClient) -> None:
        self._db = db
        self._client = client

    def get_servers(self, force_refresh: bool = False) -> tuple[list[Server], bool]:
        if not force_refresh:
            cached = self._get_cached_servers()
            if cached is not None:
                logger.info("Serving %d server(s) from cache", len(cached))
                return cached, True

        servers = self._refresh_from_ibm_pa()
        return servers, False

    def _get_cached_servers(self) -> Optional[list[Server]]:
        servers = self._db.query(Server).all()
        if not servers:
            return None
        expires = servers[0].cache_expires_at
        if not expires:
            return None
        now = datetime.now(timezone.utc)
        # SQLite retourne des datetimes naives ; on les traite comme UTC pour la comparaison.
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires > now:
            return servers
        return None

    def _refresh_from_ibm_pa(self) -> list[Server]:
        raw_servers = self._client.get_servers()
        logger.info("IBM PA returned %d server(s)", len(raw_servers))

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.ibm_pa_servers_ttl_seconds)
        now = datetime.now(timezone.utc)

        for raw in raw_servers:
            name = raw.get("Name") or raw.get("name", "")
            if not name:
                continue

            server = self._db.query(Server).filter(Server.name == name).first()
            if not server:
                server = Server(name=name)
                self._db.add(server)

            server.display_name = raw.get("DisplayName") or raw.get("display_name")
            server.host = raw.get("Host") or raw.get("host")
            server.http_port = raw.get("HTTPPort") or raw.get("http_port")
            server.is_local = raw.get("IsLocal") if "IsLocal" in raw else raw.get("is_local")
            server.accepting_clients = raw.get("AcceptingClients") if "AcceptingClients" in raw else raw.get("accepting_clients")
            server.href = raw.get("Href") or raw.get("href")
            server.is_v12 = raw.get("isV12") if "isV12" in raw else raw.get("is_v12")
            server.raw_data = json.dumps(raw)
            server.last_synced_at = now
            server.cache_expires_at = expires_at

        self._db.commit()
        return self._db.query(Server).all()
