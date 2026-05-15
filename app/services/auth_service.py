import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.clients.ibm_pa import (
    IBMPAAuthError,
    IBMPAClient,
    IBMPAConnectionError,
    IBMPAError,
    IBMPAServerError,
    IBMPATimeoutError,
)
from app.config import settings
from app.models.magic_link_token import MagicLinkToken
from app.models.user import User
from app.models.user_allowlist import UserAllowlist
from app.models.user_session import UserSession
from app.security.encryption import decrypt, encrypt

logger = logging.getLogger(__name__)


class AuthServiceError(Exception):
    pass


class InvalidCredentialsError(AuthServiceError):
    pass


class IBMPAUnreachableError(AuthServiceError):
    pass


class InvalidTokenError(AuthServiceError):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def encrypt_credentials(self, payload: dict) -> str:
        return encrypt(json.dumps(payload))

    def decrypt_credentials(self, ciphertext: str) -> dict:
        return json.loads(decrypt(ciphertext))

    def check_allowlist(self, email: str) -> bool:
        entry = self._db.query(UserAllowlist).filter(UserAllowlist.email == email).first()
        return entry is not None

    @staticmethod
    def validate_ibm_pa_credentials(tenant_id: str, api_key: str) -> None:
        client = IBMPAClient(
            base_url=settings.ibm_pa_base_url,
            tenant_id=tenant_id,
            api_key=api_key,
        )
        try:
            client.get_servers()
        except IBMPAAuthError as exc:
            raise InvalidCredentialsError("Clé API IBM PA invalide. Vérifiez votre api_key.") from exc
        except (IBMPATimeoutError, IBMPAConnectionError) as exc:
            raise IBMPAUnreachableError(
                "Impossible de joindre IBM PA pour valider les credentials. Réessayez."
            ) from exc
        except IBMPAServerError as exc:
            raise IBMPAUnreachableError(f"Erreur IBM PA {exc.status_code}.") from exc
        except IBMPAError as exc:
            raise IBMPAUnreachableError(str(exc)) from exc

    def create_or_update_user(
        self, email: str, ibm_pa_version: str, credentials_payload: dict
    ) -> User:
        encrypted = self.encrypt_credentials(credentials_payload)
        user = self._db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                ibm_pa_version=ibm_pa_version,
                credentials_encrypted=encrypted,
            )
            self._db.add(user)
        else:
            user.ibm_pa_version = ibm_pa_version
            user.credentials_encrypted = encrypted
        self._db.commit()
        self._db.refresh(user)
        logger.info("User upserted: %s (version=%s)", email, ibm_pa_version)
        return user

    def get_session_by_token(self, token: str) -> Optional[UserSession]:
        return self._db.query(UserSession).filter(
            UserSession.session_token == token
        ).first()

    def create_magic_link(
        self, email: str, ibm_pa_version: str, credentials_encrypted: str
    ) -> MagicLinkToken:
        token_str = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.auth_magic_link_ttl_minutes
        )
        token = MagicLinkToken(
            token=token_str,
            email=email,
            ibm_pa_version=ibm_pa_version,
            credentials_encrypted=credentials_encrypted,
            expires_at=expires_at,
        )
        self._db.add(token)
        self._db.commit()
        self._db.refresh(token)
        return token

    # POC: les trois opérations (marquage token, upsert User, création session)
    # devraient être atomiques en production. Voir decisions.md.
    def verify_magic_link(self, token_str: str) -> UserSession:
        token = self._db.query(MagicLinkToken).filter(
            MagicLinkToken.token == token_str
        ).first()
        if not token:
            raise InvalidTokenError()
        if token.used_at is not None:
            raise InvalidTokenError()
        expires = token.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            raise InvalidTokenError()

        token.used_at = datetime.now(timezone.utc)

        user = self.create_or_update_user(
            email=token.email,
            ibm_pa_version=token.ibm_pa_version,
            credentials_payload=self.decrypt_credentials(token.credentials_encrypted),
        )

        session_token = secrets.token_urlsafe(32)
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=datetime.now(timezone.utc) + timedelta(
                hours=settings.auth_session_ttl_hours
            ),
        )
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)
        return session
