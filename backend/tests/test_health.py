"""Pruebas mínimas de disponibilidad."""
from fastapi.testclient import TestClient
from app.main import app


def test_health() -> None:
    """El endpoint de salud responde correctamente."""
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
