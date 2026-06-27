from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.clients.ibm_pa import IBMPAAuthError, IBMPAConnectionError
from app.models.magic_link_token import MagicLinkToken

_GENERIC_REQUEST_MESSAGE = (
    "Si votre email est autorisé et vos credentials valides, "
    "un lien de connexion a été envoyé."
)

_VALID_BODY = {
    "email": "test@example.com",
    "ibm_pa_version": "V12",
    "credentials_payload": {"tenant_id": "test-tenant", "api_key": "test-key"},
}


# ---------------------------------------------------------------------------
# POST /api/v1/auth/request
# ---------------------------------------------------------------------------


def test_request_email_autorise_credentials_valides(client, db_session, make_allowlist_entry):
    make_allowlist_entry(email="test@example.com")
    with patch("app.services.auth_service.IBMPAClient") as MockClient:
        MockClient.return_value.get_servers.return_value = []
        response = client.post("/api/v1/auth/request", json=_VALID_BODY)

    assert response.status_code == 200
    assert response.json()["message"] == _GENERIC_REQUEST_MESSAGE
    assert db_session.query(MagicLinkToken).count() == 1


def test_request_email_absent_de_allowlist(client, db_session):
    response = client.post("/api/v1/auth/request", json=_VALID_BODY)

    assert response.status_code == 200
    assert response.json()["message"] == _GENERIC_REQUEST_MESSAGE
    assert db_session.query(MagicLinkToken).count() == 0


def test_request_credentials_invalides(client, make_allowlist_entry):
    make_allowlist_entry(email="test@example.com")
    with patch("app.services.auth_service.IBMPAClient") as MockClient:
        MockClient.return_value.get_servers.side_effect = IBMPAAuthError("401")
        response = client.post("/api/v1/auth/request", json=_VALID_BODY)

    assert response.status_code == 400
    assert "detail" in response.json()


def test_request_ibm_pa_injoignable(client, make_allowlist_entry):
    make_allowlist_entry(email="test@example.com")
    with patch("app.services.auth_service.IBMPAClient") as MockClient:
        MockClient.return_value.get_servers.side_effect = IBMPAConnectionError("connexion refusée")
        response = client.post("/api/v1/auth/request", json=_VALID_BODY)

    assert response.status_code == 400
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# GET /api/v1/auth/verify
# ---------------------------------------------------------------------------


def test_verify_token_valide(client, make_magic_link_token):
    token = make_magic_link_token(email="test@example.com")
    response = client.get(f"/api/v1/auth/verify?token={token.token}")

    assert response.status_code == 200
    assert response.json()["message"] == "Session créée. Vous êtes authentifié."
    # httponly ne bloque pas l'accès depuis httpx/TestClient, mais on vérifie
    # l'en-tête brut en repli au cas où response.cookies n'exposerait pas le cookie.
    cookie_value = response.cookies.get("session_token")
    if cookie_value is None:
        set_cookie_header = response.headers.get("set-cookie", "")
        assert "session_token=" in set_cookie_header
    else:
        assert cookie_value


def test_verify_token_inexistant(client):
    response = client.get("/api/v1/auth/verify?token=token-qui-nexiste-pas")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalide ou expiré."


def test_verify_token_deja_utilise(client, make_magic_link_token):
    token = make_magic_link_token(used_at=datetime.now(timezone.utc))
    response = client.get(f"/api/v1/auth/verify?token={token.token}")

    assert response.status_code == 401


def test_verify_token_expire(client, make_magic_link_token):
    token = make_magic_link_token(
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)
    )
    response = client.get(f"/api/v1/auth/verify?token={token.token}")

    assert response.status_code == 401
