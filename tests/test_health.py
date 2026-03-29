"""Basic smoke tests for the FastAPI app."""

from fastapi.testclient import TestClient

from src.api.main import app


def test_health_endpoint():
    """Health endpoint returns 200 with expected payload."""
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "praxisiq"
