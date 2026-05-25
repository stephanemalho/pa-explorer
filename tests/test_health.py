from datetime import datetime


def test_health_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_has_required_fields(client):
    data = client.get("/api/v1/health").json()
    assert "status" in data
    assert "app_name" in data
    assert "version" in data
    assert "database" in data
    assert "timestamp" in data


def test_health_status_is_ok(client):
    data = client.get("/api/v1/health").json()
    assert data["status"] == "ok"


def test_health_database_is_connected(client):
    data = client.get("/api/v1/health").json()
    assert data["database"] == "connected"


def test_health_timestamp_is_iso_format(client):
    data = client.get("/api/v1/health").json()
    datetime.fromisoformat(data["timestamp"])
