async def test_incident_audit_filter_and_csv_export(client, auth_headers):
    admin = auth_headers["administrador"]
    mesero = auth_headers["mesero"]
    table = (await client.post("/api/v1/mesas", json={"numero_mesa": 401, "zona": "Salón", "capacidad": 4}, headers=admin)).json()
    dish = (await client.post("/api/v1/menu", json={"nombre": "Prueba auditoría", "categoria": "Prueba", "precio": 15000, "tiempo_estimado_min": 10}, headers=admin)).json()
    order = (await client.post("/api/v1/pedidos", json={"id_mesa": table["id_mesa"], "detalles": [{"id_plato": dish["id_plato"], "cantidad": 1}]}, headers=mesero)).json()

    incident = await client.post("/api/v1/incidencias", json={
        "id_pedido": order["id_pedido"],
        "tipo_error": "Servicio",
        "descripcion": "Demora reportada por el mesero",
        "prioridad": "ALTA",
    }, headers=mesero)
    assert incident.status_code == 200
    assert incident.json()["estado"] == "ABIERTA"

    listed = await client.get("/api/v1/incidencias", headers=admin)
    assert listed.status_code == 200
    assert any(item["descripcion"] == "Demora reportada por el mesero" for item in listed.json())

    timing = await client.get("/api/v1/reportes/tiempos", headers=admin)
    assert timing.status_code == 200
    assert "promedio_segundos" in timing.json()

    exported = await client.get("/api/v1/reportes/exportar", headers=admin)
    assert exported.status_code == 200
    assert "text/csv" in exported.headers["content-type"]
    assert "id_pedido" in exported.text
