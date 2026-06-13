import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.models.magic_link_token import MagicLinkToken
from app.models.user import User
from app.models.user_allowlist import UserAllowlist
from app.models.user_session import UserSession
from app.security.encryption import encrypt


@pytest.fixture
def credentials_payload():
    return {"tenant_id": "test-tenant", "api_key": "test-api-key"}


@pytest.fixture
def make_allowlist_entry(db_session):
    def _make_allowlist_entry(email: str = "test@example.com") -> UserAllowlist:
        entry = UserAllowlist(email=email)
        db_session.add(entry)
        db_session.commit()
        db_session.refresh(entry)
        return entry

    return _make_allowlist_entry


@pytest.fixture
def make_user(db_session, credentials_payload):
    def _make_user(
        email: str = "test@example.com",
        ibm_pa_version: str = "V12",
        credentials: dict | None = None,
    ) -> User:
        payload = credentials if credentials is not None else credentials_payload
        user = User(
            email=email,
            ibm_pa_version=ibm_pa_version,
            credentials_encrypted=encrypt(json.dumps(payload)),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make_user


@pytest.fixture
def make_user_session(db_session, make_user):
    def _make_user_session(
        user: User | None = None,
        session_token: str | None = None,
        expires_at: datetime | None = None,
    ) -> UserSession:
        session_user = user if user is not None else make_user()
        user_session = UserSession(
            user_id=session_user.id,
            session_token=session_token or f"session-{uuid4().hex}",
            expires_at=expires_at
            or datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db_session.add(user_session)
        db_session.commit()
        db_session.refresh(user_session)
        return user_session

    return _make_user_session


@pytest.fixture
def make_magic_link_token(db_session, credentials_payload):
    def _make_magic_link_token(
        email: str = "test@example.com",
        ibm_pa_version: str = "V12",
        credentials: dict | None = None,
        expires_at: datetime | None = None,
        used_at: datetime | None = None,
        token: str | None = None,
    ) -> MagicLinkToken:
        payload = credentials if credentials is not None else credentials_payload
        magic_link = MagicLinkToken(
            token=token or f"magic-{uuid4().hex}",
            email=email,
            ibm_pa_version=ibm_pa_version,
            credentials_encrypted=encrypt(json.dumps(payload)),
            expires_at=expires_at
            or datetime.now(timezone.utc) + timedelta(minutes=15),
            used_at=used_at,
        )
        db_session.add(magic_link)
        db_session.commit()
        db_session.refresh(magic_link)
        return magic_link

    return _make_magic_link_token
