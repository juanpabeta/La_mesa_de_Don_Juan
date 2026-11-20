from decimal import Decimal


async def test_order_freezes_price_and_table_collision_returns_409(client, auth_headers):
    admin = auth_headers["administrador"]
    mesero = auth_headers["mesero"]

    table = (await client.post("/api/v1/mesas", json={
        "numero_mesa": 201,
        "zona": "Salón",
        "capacidad": 4,
    }, headers=admin)).json()
    dish = (await client.post("/api/v1/menu", json={
        "nombre": "Bandeja Paisa",
        "categoria": "Platos fuertes",
        "precio": 36000,
        "tiempo_estimado_min": 30,
    }, headers=admin)).json()

    created = await client.post("/api/v1/pedidos", json={
        "id_mesa": table["id_mesa"],
        "detalles": [{"id_plato": dish["id_plato"], "cantidad": 2, "observaciones": "Sin aguacate"}],
    }, headers=mesero)
    assert created.status_code == 200
    order = created.json()
    assert Decimal(str(order["detalles"][0]["precio_unitario"])) == Decimal("36000")

    changed = await client.put(f"/api/v1/menu/{dish['id_plato']}", json={
        "nombre": "Bandeja Paisa",
        "categoria": "Platos fuertes",
        "precio": 40000,
        "tiempo_estimado_min": 30,
    }, headers=admin)
    assert changed.status_code == 200

    reread = await client.get("/api/v1/pedidos", headers=mesero)
    persisted = next(item for item in reread.json() if item["id_pedido"] == order["id_pedido"])
    assert Decimal(str(persisted["detalles"][0]["precio_unitario"])) == Decimal("36000")

    collision = await client.post("/api/v1/pedidos", json={
        "id_mesa": table["id_mesa"],
        "detalles": [{"id_plato": dish["id_plato"], "cantidad": 1}],
    }, headers=mesero)
    assert collision.status_code == 409
    assert "no está disponible" in collision.json()["detail"].lower()


async def test_order_rejects_sold_out_or_missing_dish(client, auth_headers):
    admin = auth_headers["administrador"]
    mesero = auth_headers["mesero"]
    table = (await client.post("/api/v1/mesas", json={
        "numero_mesa": 202,
        "zona": "Barra",
        "capacidad": 2,
    }, headers=admin)).json()
    dish = (await client.post("/api/v1/menu", json={
        "nombre": "Sancocho",
        "categoria": "Sopas",
        "precio": 30000,
        "tiempo_estimado_min": 35,
    }, headers=admin)).json()
    await client.patch(
        f"/api/v1/menu/{dish['id_plato']}/agotado",
        json={"agotado": True},
        headers=auth_headers["cocina"],
    )

    response = await client.post("/api/v1/pedidos", json={
        "id_mesa": table["id_mesa"],
        "detalles": [{"id_plato": dish["id_plato"], "cantidad": 1}],
    }, headers=mesero)
    assert response.status_code == 400
