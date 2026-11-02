from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.incidencias.models import IncidenciaPedido


def test_incident_create_list_export_and_soft_delete(
    admin_client: TestClient,
    seeded_users,
    test_session_factory: sessionmaker,
) -> None:
    created = admin_client.post(
        "/api/v1/incidencias",
        json={"tipo": "OTRA", "descripcion": "Incidencia de prueba auditable"},
    )
    assert created.status_code == 201
    incident_id = created.json()["id"]
    assert created.json()["registrada_por_id"] == seeded_users["admin"]["id"]

    listed = admin_client.get("/api/v1/incidencias")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [incident_id]

    exported = admin_client.get("/api/v1/reportes/exportar")
    assert exported.status_code == 200
    assert "incidencias.csv" in exported.headers["content-disposition"]
    assert "Incidencia de prueba auditable" in exported.content.decode("utf-8-sig")

    deleted = admin_client.delete(f"/api/v1/incidencias/{incident_id}")
    assert deleted.status_code == 200
    assert admin_client.get("/api/v1/incidencias").json() == []
    with test_session_factory() as db:
        incident = db.get(IncidenciaPedido, incident_id)
        assert incident.eliminada_en is not None
        assert incident.eliminada_por_id == seeded_users["admin"]["id"]


def test_reports_reject_inverted_date_range(admin_client: TestClient) -> None:
    response = admin_client.get("/api/v1/reportes/tiempos?desde=2026-12-31&hasta=2026-01-01")
    assert response.status_code == 422


def test_incident_creation_is_admin_only(client: TestClient, seeded_users) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"correo": seeded_users["mesero"]["email"], "contrasena": seeded_users["mesero"]["password"]},
    )
    assert login.status_code == 200
    response = client.post(
        "/api/v1/incidencias",
        json={"tipo": "OTRA", "descripcion": "Incidencia sin autorización"},
    )
    assert response.status_code == 403
