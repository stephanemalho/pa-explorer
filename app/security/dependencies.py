import json
import logging
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.clients.ibm_pa import IBMPAClient
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.user_session import UserSession
from app.security.encryption import decrypt

logger = logging.getLogger(__name__)

_INVALID_SESSION_MSG = "Session invalide ou expirée."


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail=_INVALID_SESSION_MSG)

    session = db.query(UserSession).filter(UserSession.session_token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail=_INVALID_SESSION_MSG)

    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail=_INVALID_SESSION_MSG)

    session.last_used_at = datetime.now(timezone.utc)
    db.commit()

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail=_INVALID_SESSION_MSG)
    return user


def get_ibm_pa_client_for_user(user: User = Depends(get_current_user)) -> IBMPAClient:
    credentials = json.loads(decrypt(user.credentials_encrypted))
    if user.ibm_pa_version == "V12":
        return IBMPAClient(
            base_url=settings.ibm_pa_base_url,
            tenant_id=credentials["tenant_id"],
            api_key=credentials["api_key"],
        )
    raise HTTPException(
        status_code=501,
        detail=f"Version IBM PA non supportée : {user.ibm_pa_version}",
    )
