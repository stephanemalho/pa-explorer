from datetime import datetime, timedelta, timezone

import pytest

from app.clients.ibm_pa import IBMPAAuthError
from app.models.dimension import Dimension
from app.services.dimension_service import DimensionService
from tests.fakes import FAKE_DIMENSIONS, FakeIBMPAClient

SERVER_NAME = "SalesServer"
CUBE_NAME = "SalesCube"


def test_get_dimensions_cache_miss_calls_client(db_session):
    fake_client = FakeIBMPAClient()
    service = DimensionService(db=db_session, client=fake_client)

    dimensions, from_cache = service.get_dimensions(SERVER_NAME, CUBE_NAME)

    assert from_cache is False
    assert fake_client.get_dimensions_call_count == 1
    assert len(dimensions) == len(FAKE_DIMENSIONS)
    assert {d.name for d in dimensions} == {d["Name"] for d in FAKE_DIMENSIONS}


def test_get_dimensions_cache_hit_skips_client(db_session):
    fake_client = FakeIBMPAClient()
    service = DimensionService(db=db_session, client=fake_client)

    service.get_dimensions(SERVER_NAME, CUBE_NAME)  # premier appel — peuple la base
    dimensions, from_cache = service.get_dimensions(SERVER_NAME, CUBE_NAME)  # doit servir le cache

    assert from_cache is True
    assert fake_client.get_dimensions_call_count == 1


def test_get_dimensions_expired_cache_recalls_client(db_session):
    past = datetime.now(timezone.utc) - timedelta(seconds=600)
    db_session.add(
        Dimension(name="Product", server_name=SERVER_NAME, cube_name=CUBE_NAME, cache_expires_at=past)
    )
    db_session.commit()

    fake_client = FakeIBMPAClient()
    service = DimensionService(db=db_session, client=fake_client)

    dimensions, from_cache = service.get_dimensions(SERVER_NAME, CUBE_NAME)

    assert from_cache is False
    assert fake_client.get_dimensions_call_count == 1
    assert {d.name for d in dimensions} == {d["Name"] for d in FAKE_DIMENSIONS}


def test_get_dimensions_force_refresh_bypasses_cache(db_session):
    fake_client = FakeIBMPAClient()
    service = DimensionService(db=db_session, client=fake_client)

    service.get_dimensions(SERVER_NAME, CUBE_NAME)  # premier appel — peuple le cache
    assert fake_client.get_dimensions_call_count == 1

    _, from_cache = service.get_dimensions(SERVER_NAME, CUBE_NAME, force_refresh=True)

    assert from_cache is False
    assert fake_client.get_dimensions_call_count == 2


def test_get_dimensions_propagates_auth_error(db_session):
    fake_client = FakeIBMPAClient(raise_error=IBMPAAuthError("Clé invalide"))
    service = DimensionService(db=db_session, client=fake_client)

    with pytest.raises(IBMPAAuthError):
        service.get_dimensions(SERVER_NAME, CUBE_NAME)


def test_get_dimensions_passes_both_params_to_client(db_session):
    fake_client = FakeIBMPAClient()
    service = DimensionService(db=db_session, client=fake_client)

    service.get_dimensions("MonServeur", "MonCube")

    assert fake_client.last_dimension_server_name == "MonServeur"
    assert fake_client.last_dimension_cube_name == "MonCube"
