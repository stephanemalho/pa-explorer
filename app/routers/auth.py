import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import AuthRequest, AuthRequestResponse, AuthVerifyResponse
from app.services.auth_service import (
    AuthService,
    IBMPAUnreachableError,
    InvalidCredentialsError,
    InvalidTokenError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

_GENERIC_REQUEST_MESSAGE = (
    "Si votre email est autorisé et vos credentials valides, "
    "un lien de connexion a été envoyé."
)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db=db)


@router.post("/auth/request", response_model=AuthRequestResponse)
def request_magic_link(
    body: AuthRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> AuthRequestResponse:
    email = str(body.email)

    if not service.check_allowlist(email):
        logger.debug("Auth request pour email non autorisé (détail masqué).")
        return AuthRequestResponse(message=_GENERIC_REQUEST_MESSAGE)

    tenant_id = body.credentials_payload.get("tenant_id", "")
    api_key = body.credentials_payload.get("api_key", "")
    try:
        AuthService.validate_ibm_pa_credentials(tenant_id, api_key)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IBMPAUnreachableError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    credentials_encrypted = service.encrypt_credentials(body.credentials_payload)
    token = service.create_magic_link(email, body.ibm_pa_version, credentials_encrypted)

    verify_url = f"{request.base_url}api/v1/auth/verify?token={token.token}"
    logger.info("Magic link émis pour %s : %s", email, verify_url)

    return AuthRequestResponse(message=_GENERIC_REQUEST_MESSAGE)


@router.get("/auth/verify", response_model=AuthVerifyResponse)
def verify_magic_link_endpoint(
    response: Response,
    token: str = Query(description="Token du magic link"),
    service: AuthService = Depends(get_auth_service),
) -> AuthVerifyResponse:
    try:
        session = service.verify_magic_link(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")
    response.set_cookie(
        key="session_token",
        value=session.session_token,
        httponly=True,
        samesite="lax",
        max_age=86400,
        secure=False,  # HTTP dev local — passer à True en production HTTPS
    )
    return AuthVerifyResponse(message="Session créée. Vous êtes authentifié.")
