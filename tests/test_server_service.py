from datetime import datetime, timedelta, timezone

import pytest

from app.clients.ibm_pa import IBMPAAuthError
from app.models.server import Server
from app.services.server_service import ServerService
from tests.fakes import FAKE_SERVERS, FakeIBMPAClient


def test_get_servers_cache_miss_calls_client(db_session):
    fake_client = FakeIBMPAClient()
    service = ServerService(db=db_session, client=fake_client)

    servers, from_cache = service.get_servers()

    assert from_cache is False
    assert fake_client.get_servers_call_count == 1
    assert len(servers) == len(FAKE_SERVERS)
    assert {s.name for s in servers} == {d["Name"] for d in FAKE_SERVERS}


def test_get_servers_cache_hit_skips_client(db_session):
    fake_client = FakeIBMPAClient()
    service = ServerService(db=db_session, client=fake_client)

    service.get_servers()  # premier appel — peuple la base et le cache
    servers, from_cache = service.get_servers()  # second appel — doit servir le cache

    assert from_cache is True
    assert fake_client.get_servers_call_count == 1


def test_get_servers_expired_cache_recalls_client(db_session):
    past = datetime.now(timezone.utc) - timedelta(seconds=600)
    db_session.add(Server(name="SalesServer", cache_expires_at=past))
    db_session.commit()

    fake_client = FakeIBMPAClient()
    service = ServerService(db=db_session, client=fake_client)

    servers, from_cache = service.get_servers()

    assert from_cache is False
    assert fake_client.get_servers_call_count == 1
    assert {s.name for s in servers} == {d["Name"] for d in FAKE_SERVERS}


def test_get_servers_force_refresh_bypasses_cache(db_session):
    fake_client = FakeIBMPAClient()
    service = ServerService(db=db_session, client=fake_client)

    service.get_servers()  # premier appel — peuple le cache
    assert fake_client.get_servers_call_count == 1

    _, from_cache = service.get_servers(force_refresh=True)

    assert from_cache is False
    assert fake_client.get_servers_call_count == 2


def test_get_servers_propagates_auth_error(db_session):
    fake_client = FakeIBMPAClient(raise_error=IBMPAAuthError("Clé invalide"))
    service = ServerService(db=db_session, client=fake_client)

    with pytest.raises(IBMPAAuthError):
        service.get_servers()
