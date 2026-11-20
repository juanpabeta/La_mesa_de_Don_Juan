from unittest.mock import AsyncMock

import app.modules.pedidos.routes as pedido_routes


async def test_kds_state_transitions_and_printer_failure_is_resilient(client, auth_headers, monkeypatch):
    admin = auth_headers["administrador"]
    mesero = auth_headers["mesero"]
    cocina = auth_headers["cocina"]
    table = (await client.post("/api/v1/mesas", json={
        "numero_mesa": 301,
        "zona": "Salón",
        "capacidad": 4,
    }, headers=admin)).json()
    dish = (await client.post("/api/v1/menu", json={
        "nombre": "E2E Sancocho",
        "categoria": "Sopas",
        "precio": 30000,
        "tiempo_estimado_min": 35,
    }, headers=admin)).json()

    monkeypatch.setattr(pedido_routes, "print_ticket", AsyncMock(side_effect=ConnectionError("printer unavailable")))
    created = await client.post("/api/v1/pedidos", json={
        "id_mesa": table["id_mesa"],
        "detalles": [{"id_plato": dish["id_plato"], "cantidad": 1}],
    }, headers=mesero)
    assert created.status_code == 200
    order = created.json()

    preparing = await client.patch(
        f"/api/v1/pedidos/{order['id_pedido']}/estado",
        json={"estado": "EN_PREPARACION"},
        headers=cocina,
    )
    assert preparing.status_code == 200
    assert preparing.json()["estado"] == "EN_PREPARACION"

    ready = await client.patch(
        f"/api/v1/pedidos/{order['id_pedido']}/estado",
        json={"estado": "LISTO"},
        headers=cocina,
    )
    assert ready.status_code == 200

    delivered = await client.patch(
        f"/api/v1/pedidos/{order['id_pedido']}/estado",
        json={"estado": "ENTREGADO"},
        headers=mesero,
    )
    assert delivered.status_code == 200
    assert delivered.json()["fecha_hora_entrega"] is not None

    table_after = await client.get("/api/v1/mesas", headers=mesero)
    assert next(item for item in table_after.json() if item["id_mesa"] == table["id_mesa"])["estado"] == "Disponible"

    incidences = await client.get("/api/v1/incidencias", headers=admin)
    assert incidences.status_code == 200
    assert any(item["tipo_error"] == "Falla de impresora" for item in incidences.json())


async def test_reprint_printer_failure_records_audit(client, auth_headers, monkeypatch):
    admin = auth_headers["administrador"]
    mesero = auth_headers["mesero"]
    table = (await client.post("/api/v1/mesas", json={"numero_mesa": 302, "zona": "Salón", "capacidad": 4}, headers=admin)).json()
    dish = (await client.post("/api/v1/menu", json={"nombre": "Reimpresión", "categoria": "Prueba", "precio": 1000, "tiempo_estimado_min": 5}, headers=admin)).json()
    order = (await client.post("/api/v1/pedidos", json={"id_mesa": table["id_mesa"], "detalles": [{"id_plato": dish["id_plato"], "cantidad": 1}]}, headers=mesero)).json()

    monkeypatch.setattr(pedido_routes, "print_ticket", AsyncMock(side_effect=ConnectionError("offline")))
    response = await client.post(f"/api/v1/pedidos/{order['id_pedido']}/reimprimir", headers=mesero)
    assert response.status_code == 503

    audit = await client.get("/api/v1/incidencias", headers=admin)
    assert any(item["tipo_error"] == "Falla de impresora" for item in audit.json())
