from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.clients.ibm_pa import (
    IBMPAAuthError,
    IBMPAConnectionError,
    IBMPAServerError,
    IBMPATimeoutError,
)
from app.services.auth_service import (
    AuthService,
    IBMPAUnreachableError,
    InvalidCredentialsError,
    InvalidTokenError,
)


# ---------------------------------------------------------------------------
# check_allowlist
# ---------------------------------------------------------------------------


def test_check_allowlist_email_present(db_session, make_allowlist_entry):
    make_allowlist_entry(email="user@example.com")
    service = AuthService(db_session)
    assert service.check_allowlist("user@example.com") is True


def test_check_allowlist_email_absent(db_session):
    service = AuthService(db_session)
    assert service.check_allowlist("absent@example.com") is False


# ---------------------------------------------------------------------------
# create_or_update_user
# ---------------------------------------------------------------------------


def test_create_or_update_user_creates_new(db_session, credentials_payload):
    service = AuthService(db_session)
    user = service.create_or_update_user("new@example.com", "V12", credentials_payload)

    assert user.id is not None
    assert user.email == "new@example.com"
    assert user.ibm_pa_version == "V12"
    # credentials_encrypted doit être chiffré (pas en clair)
    assert user.credentials_encrypted != str(credentials_payload)


def test_create_or_update_user_updates_existing(db_session, make_user, credentials_payload):
    make_user(email="existing@example.com", ibm_pa_version="V11")
    service = AuthService(db_session)

    updated = service.create_or_update_user(
        "existing@example.com", "V12", {"tenant_id": "new-tenant", "api_key": "new-key"}
    )

    assert updated.ibm_pa_version == "V12"
    decrypted = service.decrypt_credentials(updated.credentials_encrypted)
    assert decrypted["tenant_id"] == "new-tenant"


# ---------------------------------------------------------------------------
# create_magic_link
# ---------------------------------------------------------------------------


def test_create_magic_link_stores_token(db_session):
    service = AuthService(db_session)
    encrypted = service.encrypt_credentials({"tenant_id": "t", "api_key": "k"})
    token = service.create_magic_link("user@example.com", "V12", encrypted)

    assert token.id is not None
    assert token.email == "user@example.com"
    assert token.ibm_pa_version == "V12"
    assert token.used_at is None
    # SQLite supprime le tzinfo — normaliser avant comparaison (piège CLAUDE.md)
    expires = token.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    assert expires > datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# get_session_by_token
# ---------------------------------------------------------------------------


def test_get_session_by_token_found(db_session, make_user_session):
    session = make_user_session(session_token="tok-abc")
    service = AuthService(db_session)
    result = service.get_session_by_token("tok-abc")
    assert result is not None
    assert result.id == session.id


def test_get_session_by_token_not_found(db_session):
    service = AuthService(db_session)
    assert service.get_session_by_token("inexistant") is None


# ---------------------------------------------------------------------------
# verify_magic_link
# ---------------------------------------------------------------------------


def test_verify_magic_link_valid(db_session, make_magic_link_token):
    token = make_magic_link_token()
    service = AuthService(db_session)
    session = service.verify_magic_link(token.token)

    assert session.id is not None
    assert session.session_token is not None
    # le token doit être marqué comme utilisé
    db_session.refresh(token)
    assert token.used_at is not None


def test_verify_magic_link_token_not_found(db_session):
    service = AuthService(db_session)
    with pytest.raises(InvalidTokenError):
        service.verify_magic_link("inexistant-token")


def test_verify_magic_link_already_used(db_session, make_magic_link_token):
    token = make_magic_link_token(used_at=datetime.now(timezone.utc))
    service = AuthService(db_session)
    with pytest.raises(InvalidTokenError):
        service.verify_magic_link(token.token)


def test_verify_magic_link_expired(db_session, make_magic_link_token):
    token = make_magic_link_token(
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)
    )
    service = AuthService(db_session)
    with pytest.raises(InvalidTokenError):
        service.verify_magic_link(token.token)


# ---------------------------------------------------------------------------
# validate_ibm_pa_credentials (méthode statique, instancie IBMPAClient directement)
# ---------------------------------------------------------------------------


def test_validate_credentials_success():
    with patch("app.services.auth_service.IBMPAClient") as MockClient:
        MockClient.return_value.get_servers.return_value = []
        AuthService.validate_ibm_pa_credentials("tenant-x", "key-y")
        MockClient.return_value.get_servers.assert_called_once()


def test_validate_credentials_auth_error():
    with patch("app.services.auth_service.IBMPAClient") as MockClient:
        MockClient.return_value.get_servers.side_effect = IBMPAAuthError("401")
        with pytest.raises(InvalidCredentialsError):
            AuthService.validate_ibm_pa_credentials("tenant-x", "bad-key")


def test_validate_credentials_timeout():
    with patch("app.services.auth_service.IBMPAClient") as MockClient:
        MockClient.return_value.get_servers.side_effect = IBMPATimeoutError("timeout")
        with pytest.raises(IBMPAUnreachableError):
            AuthService.validate_ibm_pa_credentials("tenant-x", "key-y")


def test_validate_credentials_connection_error():
    with patch("app.services.auth_service.IBMPAClient") as MockClient:
        MockClient.return_value.get_servers.side_effect = IBMPAConnectionError("conn")
        with pytest.raises(IBMPAUnreachableError):
            AuthService.validate_ibm_pa_credentials("tenant-x", "key-y")


def test_validate_credentials_server_error():
    with patch("app.services.auth_service.IBMPAClient") as MockClient:
        err = IBMPAServerError("server error")
        err.status_code = 500
        MockClient.return_value.get_servers.side_effect = err
        with pytest.raises(IBMPAUnreachableError):
            AuthService.validate_ibm_pa_credentials("tenant-x", "key-y")
