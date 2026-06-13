from datetime import datetime, timedelta, timezone

import pytest

from app.clients.ibm_pa import IBMPAAuthError
from app.models.cube import Cube
from app.services.cube_service import CubeService
from tests.fakes import FAKE_CUBES, FakeIBMPAClient

SERVER_NAME = "SalesServer"


def test_get_cubes_cache_miss_calls_client(db_session):
    fake_client = FakeIBMPAClient()
    service = CubeService(db=db_session, client=fake_client)

    cubes, from_cache = service.get_cubes(SERVER_NAME)

    assert from_cache is False
    assert fake_client.get_cubes_call_count == 1
    assert len(cubes) == len(FAKE_CUBES)
    assert {c.name for c in cubes} == {d["Name"] for d in FAKE_CUBES}


def test_get_cubes_cache_hit_skips_client(db_session):
    fake_client = FakeIBMPAClient()
    service = CubeService(db=db_session, client=fake_client)

    service.get_cubes(SERVER_NAME)  # premier appel — peuple la base et le cache
    cubes, from_cache = service.get_cubes(SERVER_NAME)  # second appel — doit servir le cache

    assert from_cache is True
    assert fake_client.get_cubes_call_count == 1


def test_get_cubes_expired_cache_recalls_client(db_session):
    past = datetime.now(timezone.utc) - timedelta(seconds=600)
    db_session.add(Cube(name="SalesCube", server_name=SERVER_NAME, cache_expires_at=past))
    db_session.commit()

    fake_client = FakeIBMPAClient()
    service = CubeService(db=db_session, client=fake_client)

    cubes, from_cache = service.get_cubes(SERVER_NAME)

    assert from_cache is False
    assert fake_client.get_cubes_call_count == 1
    assert {c.name for c in cubes} == {d["Name"] for d in FAKE_CUBES}


def test_get_cubes_force_refresh_bypasses_cache(db_session):
    fake_client = FakeIBMPAClient()
    service = CubeService(db=db_session, client=fake_client)

    service.get_cubes(SERVER_NAME)  # premier appel — peuple le cache
    assert fake_client.get_cubes_call_count == 1

    _, from_cache = service.get_cubes(SERVER_NAME, force_refresh=True)

    assert from_cache is False
    assert fake_client.get_cubes_call_count == 2


def test_get_cubes_propagates_auth_error(db_session):
    fake_client = FakeIBMPAClient(raise_error=IBMPAAuthError("Clé invalide"))
    service = CubeService(db=db_session, client=fake_client)

    with pytest.raises(IBMPAAuthError):
        service.get_cubes(SERVER_NAME)


def test_get_cubes_passes_server_name_to_client(db_session):
    fake_client = FakeIBMPAClient()
    service = CubeService(db=db_session, client=fake_client)

    service.get_cubes("MonServeur")

    assert fake_client.last_cube_server_name == "MonServeur"
