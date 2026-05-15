import json
import logging
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
