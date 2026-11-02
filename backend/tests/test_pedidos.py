from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.mesas.models import Mesa
from app.modules.pedidos.models import Pedido


def create_order(client: TestClient) -> dict:
    table = client.post("/api/v1/mesas", json={"numero": 4, "zona": "Interior", "capacidad": 2})
    assert table.status_code == 201
    dish = client.post(
        "/api/v1/menu",
        json={"nombre": "Sopa de prueba", "precio": "9.90", "tiempo_preparacion_minutos": 5},
    )
    assert dish.status_code == 201
    order = client.post(
        "/api/v1/pedidos",
        json={"mesa_id": table.json()["id"], "detalles": [{"plato_id": dish.json()["id"], "cantidad": 1}]},
    )
    assert order.status_code == 201
    return order.json()


def test_create_order_occupies_table_and_can_be_read_by_id(admin_client: TestClient) -> None:
    order = create_order(admin_client)
    detail = admin_client.get(f"/api/v1/pedidos/{order['id']}")
    assert detail.status_code == 200
    assert detail.json()["estado"] == "PENDIENTE"

    tables = admin_client.get("/api/v1/mesas")
    assert tables.status_code == 200
    assert tables.json()[0]["estado"] == "OCUPADA"
    duplicate = admin_client.post(
        "/api/v1/pedidos",
        json={"mesa_id": order["mesa_id"], "detalles": [{"plato_id": order["detalles"][0]["plato_id"], "cantidad": 1}]},
    )
    assert duplicate.status_code == 409


def test_order_state_machine_rejects_invalid_transition(admin_client: TestClient) -> None:
    order = create_order(admin_client)
    invalid = admin_client.patch(f"/api/v1/pedidos/{order['id']}/estado", json={"estado": "LISTO"})
    assert invalid.status_code == 422
    assert admin_client.get(f"/api/v1/pedidos/{order['id']}").json()["estado"] == "PENDIENTE"


def test_ticket_endpoint_marks_overdue_orders(admin_client: TestClient, test_session_factory: sessionmaker) -> None:
    order = create_order(admin_client)
    with test_session_factory() as db:
        stored = db.get(Pedido, order["id"])
        stored.creado_en = datetime.now(UTC) - timedelta(minutes=30)
        db.commit()

    tickets = admin_client.get("/api/v1/pedidos/tickets")
    assert tickets.status_code == 200
    ticket = tickets.json()[0]
    assert ticket["retrasado"] is True
    assert ticket["minutos_transcurridos"] >= 30
    assert ticket["retraso_marcado_en"] is not None


def test_order_delete_preserves_audit_and_does_not_leave_table_occupied(
    admin_client: TestClient,
    seeded_users,
    test_session_factory: sessionmaker,
) -> None:
    order = create_order(admin_client)
    cancelled = admin_client.patch(f"/api/v1/pedidos/{order['id']}/estado", json={"estado": "CANCELADO"})
    assert cancelled.status_code == 200

    deleted = admin_client.delete(f"/api/v1/pedidos/{order['id']}")
    assert deleted.status_code == 200
    assert admin_client.get(f"/api/v1/pedidos/{order['id']}").status_code == 404

    with test_session_factory() as db:
        stored = db.get(Pedido, order["id"])
        table = db.get(Mesa, order["mesa_id"])
        assert stored.eliminado_en is not None
        assert stored.eliminado_por_id == seeded_users["admin"]["id"]
        assert table.estado == "LIBRE"
