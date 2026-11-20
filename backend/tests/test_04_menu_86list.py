async def test_menu_validation_create_and_86_toggle(client, auth_headers):
    admin = auth_headers["administrador"]
    cocina = auth_headers["cocina"]
    invalid = await client.post("/api/v1/menu", json={
        "nombre": "Inválido",
        "categoria": "Prueba",
        "precio": 0,
        "tiempo_estimado_min": 0,
    }, headers=admin)
    assert invalid.status_code == 422

    created = await client.post("/api/v1/menu", json={
        "nombre": "Ajiaco Santafereño",
        "categoria": "Sopas",
        "precio": 28000,
        "tiempo_estimado_min": 25,
    }, headers=admin)
    assert created.status_code == 200
    dish = created.json()

    agotado = await client.patch(
        f"/api/v1/menu/{dish['id_plato']}/agotado",
        json={"agotado": True},
        headers=cocina,
    )
    assert agotado.status_code == 200
    assert agotado.json()["agotado"] is True

    reenabled = await client.patch(
        f"/api/v1/menu/{dish['id_plato']}/agotado",
        json={"agotado": False},
        headers=admin,
    )
    assert reenabled.status_code == 200
    assert reenabled.json()["agotado"] is False
