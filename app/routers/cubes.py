import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query
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
from app.models.cube import Cube
from app.schemas.cube import CubeResponse, CubesListResponse
from app.security.dependencies import get_ibm_pa_client_for_user
from app.services.cube_service import CubeService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cubes"])


def get_cube_service(
    db: Session = Depends(get_db),
    client: IBMPAClient = Depends(get_ibm_pa_client_for_user),
) -> CubeService:
    return CubeService(db=db, client=client)


def _build_response(
    cubes: list[Cube],
    from_cache: bool,
    include_raw: bool,
) -> CubesListResponse:
    cube_responses = []
    for c in cubes:
        cube_responses.append(
            CubeResponse(
                id=c.id,
                name=c.name,
                server_name=c.server_name,
                last_schema_update=c.last_schema_update,
                last_data_update=c.last_data_update,
                last_synced_at=c.last_synced_at,
                cache_expires_at=c.cache_expires_at,
                created_at=c.created_at,
                raw_data=json.loads(c.raw_data) if include_raw and c.raw_data else None,
            )
        )
    return CubesListResponse(
        cubes=cube_responses,
        count=len(cube_responses),
        from_cache=from_cache,
        cache_expires_at=cubes[0].cache_expires_at if cubes else None,
    )


def _handle_ibm_pa_error(exc: IBMPAError) -> HTTPException:
    if isinstance(exc, IBMPAAuthError):
        logger.error("IBM PA authentication failed: %s", exc)
        return HTTPException(502, detail="IBM PA authentication failed. Verify IBM_PA_API_KEY.")
    if isinstance(exc, IBMPAForbiddenError):
        logger.error("IBM PA access denied: %s", exc)
        return HTTPException(502, detail="IBM PA access denied to /Cubes endpoint.")
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


@router.get("/servers/{server_name}/cubes", response_model=CubesListResponse)
def list_cubes(
    server_name: str = Path(description="Name of the TM1 server"),
    force_refresh: bool = Query(default=False, description="Force sync from IBM PA ignoring cache TTL"),
    include_raw: bool = Query(default=False, description="Include raw IBM PA payload per cube"),
    service: CubeService = Depends(get_cube_service),
) -> CubesListResponse:
    try:
        cubes, from_cache = service.get_cubes(server_name=server_name, force_refresh=force_refresh)
    except IBMPAError as exc:
        raise _handle_ibm_pa_error(exc)
    return _build_response(cubes, from_cache, include_raw)


@router.post("/servers/{server_name}/cubes/refresh", response_model=CubesListResponse)
def refresh_cubes(
    server_name: str = Path(description="Name of the TM1 server"),
    include_raw: bool = Query(default=False, description="Include raw IBM PA payload per cube"),
    service: CubeService = Depends(get_cube_service),
) -> CubesListResponse:
    try:
        cubes, from_cache = service.get_cubes(server_name=server_name, force_refresh=True)
    except IBMPAError as exc:
        raise _handle_ibm_pa_error(exc)
    return _build_response(cubes, from_cache, include_raw)
