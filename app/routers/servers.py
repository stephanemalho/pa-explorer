import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.clients.ibm_pa import (
    IBMPAAuthError,
    IBMPAClient,
    IBMPAConnectionError,
    IBMPAError,
    IBMPAForbiddenError,
    IBMPAServerError,
    IBMPATimeoutError,
    IBMPAUnexpectedResponseError,
)
from app.config import settings
from app.database import get_db
from app.models.server import Server
from app.schemas.server import ServerResponse, ServersListResponse
from app.security.dependencies import get_ibm_pa_client_for_user
from app.services.server_service import ServerService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["servers"])


def get_server_service(
    db: Session = Depends(get_db),
    client: IBMPAClient = Depends(get_ibm_pa_client_for_user),
) -> ServerService:
    return ServerService(db=db, client=client)


def _build_response(
    servers: list[Server],
    from_cache: bool,
    include_raw: bool,
) -> ServersListResponse:
    server_responses = []
    for s in servers:
        server_responses.append(
            ServerResponse(
                id=s.id,
                name=s.name,
                display_name=s.display_name,
                host=s.host,
                http_port=s.http_port,
                is_local=s.is_local,
                accepting_clients=s.accepting_clients,
                href=s.href,
                is_v12=s.is_v12,
                last_synced_at=s.last_synced_at,
                cache_expires_at=s.cache_expires_at,
                created_at=s.created_at,
                raw_data=json.loads(s.raw_data) if include_raw and s.raw_data else None,
            )
        )
    return ServersListResponse(
        servers=server_responses,
        count=len(server_responses),
        from_cache=from_cache,
        cache_expires_at=servers[0].cache_expires_at if servers else None,
    )


def _handle_ibm_pa_error(exc: IBMPAError) -> HTTPException:
    if isinstance(exc, IBMPAAuthError):
        logger.error("IBM PA authentication failed: %s", exc)
        return HTTPException(502, detail="IBM PA authentication failed. Verify IBM_PA_API_KEY.")
    if isinstance(exc, IBMPAForbiddenError):
        logger.error("IBM PA access denied: %s", exc)
        return HTTPException(502, detail="IBM PA access denied to /Servers endpoint.")
    if isinstance(exc, IBMPATimeoutError):
        logger.warning("IBM PA request timed out: %s", exc)
        return HTTPException(504, detail="IBM PA request timed out after 30 seconds.")
    if isinstance(exc, IBMPAConnectionError):
        logger.error("Cannot reach IBM PA (%s): %s", settings.ibm_pa_base_url, exc)
        return HTTPException(503, detail="Cannot reach IBM PA. Check IBM_PA_BASE_URL.")
    if isinstance(exc, IBMPAServerError):
        logger.error("IBM PA server error %d: %s", exc.status_code, exc.body)
        return HTTPException(502, detail=f"IBM PA returned a server error: {exc.status_code}.")
    if isinstance(exc, IBMPAUnexpectedResponseError):
        logger.error("IBM PA unexpected response: %s", exc)
        return HTTPException(502, detail=str(exc))
    logger.error("Unhandled IBM PA error: %s", exc)
    return HTTPException(502, detail="Unexpected error communicating with IBM PA.")


@router.get("/servers", response_model=ServersListResponse)
def list_servers(
    force_refresh: bool = Query(default=False, description="Force sync from IBM PA ignoring cache TTL"),
    include_raw: bool = Query(default=False, description="Include raw IBM PA payload per server"),
    service: ServerService = Depends(get_server_service),
) -> ServersListResponse:
    try:
        servers, from_cache = service.get_servers(force_refresh=force_refresh)
    except IBMPAError as exc:
        raise _handle_ibm_pa_error(exc)
    return _build_response(servers, from_cache, include_raw)


@router.post("/servers/refresh", response_model=ServersListResponse)
def refresh_servers(
    include_raw: bool = Query(default=False, description="Include raw IBM PA payload per server"),
    service: ServerService = Depends(get_server_service),
) -> ServersListResponse:
    try:
        servers, from_cache = service.get_servers(force_refresh=True)
    except IBMPAError as exc:
        raise _handle_ibm_pa_error(exc)
    return _build_response(servers, from_cache, include_raw)
