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
from app.models.dimension import Dimension
from app.schemas.dimension import DimensionResponse, DimensionsListResponse
from app.services.dimension_service import DimensionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["dimensions"])


def get_ibm_pa_client() -> IBMPAClient:
    return IBMPAClient(
        base_url=settings.ibm_pa_base_url,
        tenant_id=settings.ibm_pa_tenant_id,
        api_key=settings.ibm_pa_api_key,
    )


def get_dimension_service(
    db: Session = Depends(get_db),
    client: IBMPAClient = Depends(get_ibm_pa_client),
) -> DimensionService:
    return DimensionService(db=db, client=client)


def _build_response(
    dimensions: list[Dimension],
    from_cache: bool,
    include_raw: bool,
) -> DimensionsListResponse:
    dimension_responses = []
    for d in dimensions:
        dimension_responses.append(
            DimensionResponse(
                id=d.id,
                name=d.name,
                server_name=d.server_name,
                cube_name=d.cube_name,
                unique_name=d.unique_name,
                last_synced_at=d.last_synced_at,
                cache_expires_at=d.cache_expires_at,
                created_at=d.created_at,
                raw_data=json.loads(d.raw_data) if include_raw and d.raw_data else None,
            )
        )
    return DimensionsListResponse(
        dimensions=dimension_responses,
        count=len(dimension_responses),
        from_cache=from_cache,
        cache_expires_at=dimensions[0].cache_expires_at if dimensions else None,
    )


def _handle_ibm_pa_error(exc: IBMPAError) -> HTTPException:
    if isinstance(exc, IBMPAAuthError):
        logger.error("IBM PA authentication failed: %s", exc)
        return HTTPException(502, detail="IBM PA authentication failed. Verify IBM_PA_API_KEY.")
    if isinstance(exc, IBMPAForbiddenError):
        logger.error("IBM PA access denied: %s", exc)
        return HTTPException(502, detail="IBM PA access denied to /Dimensions endpoint.")
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


@router.get(
    "/servers/{server_name}/cubes/{cube_name}/dimensions",
    response_model=DimensionsListResponse,
)
def list_dimensions(
    server_name: str = Path(description="Name of the TM1 server"),
    cube_name: str = Path(description="Name of the TM1 cube"),
    force_refresh: bool = Query(default=False, description="Force sync from IBM PA ignoring cache TTL"),
    include_raw: bool = Query(default=False, description="Include raw IBM PA payload per dimension"),
    service: DimensionService = Depends(get_dimension_service),
) -> DimensionsListResponse:
    try:
        dimensions, from_cache = service.get_dimensions(
            server_name=server_name, cube_name=cube_name, force_refresh=force_refresh
        )
    except IBMPAError as exc:
        raise _handle_ibm_pa_error(exc)
    return _build_response(dimensions, from_cache, include_raw)


@router.post(
    "/servers/{server_name}/cubes/{cube_name}/dimensions/refresh",
    response_model=DimensionsListResponse,
)
def refresh_dimensions(
    server_name: str = Path(description="Name of the TM1 server"),
    cube_name: str = Path(description="Name of the TM1 cube"),
    include_raw: bool = Query(default=False, description="Include raw IBM PA payload per dimension"),
    service: DimensionService = Depends(get_dimension_service),
) -> DimensionsListResponse:
    try:
        dimensions, from_cache = service.get_dimensions(
            server_name=server_name, cube_name=cube_name, force_refresh=True
        )
    except IBMPAError as exc:
        raise _handle_ibm_pa_error(exc)
    return _build_response(dimensions, from_cache, include_raw)
