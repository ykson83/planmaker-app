from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_serves_dashboard() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "<title>Bakii" in response.text


def test_unknown_route_returns_not_found() -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
