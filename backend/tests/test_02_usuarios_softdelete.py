async def test_crud_employee_duplicate_email_and_soft_delete(client, auth_headers):
    headers = auth_headers["administrador"]
    payload = {
        "nombres": "Ana",
        "apellidos": "Prueba",
        "correo": "ana.qa@gmail.com",
        "contraseña": "Secreto123!",
        "roles": ["Mesero"],
    }
    created = await client.post("/api/v1/usuarios", json=payload, headers=headers)
    assert created.status_code == 200
    employee = created.json()
    assert employee["estado"] is True

    duplicate = await client.post("/api/v1/usuarios", json=payload, headers=headers)
    assert duplicate.status_code == 409
    assert "correo" in duplicate.json()["detail"].lower()

    updated = await client.put(
        f"/api/v1/usuarios/{employee['id_usuario']}",
        json={"nombres": "Ana Actualizada", "roles": ["Cocinero"]},
        headers=headers,
    )
    assert updated.status_code == 200
    assert "Cocinero" in updated.json()["roles"]

    deleted = await client.delete(
        f"/api/v1/usuarios/{employee['id_usuario']}",
        headers=headers,
    )
    assert deleted.status_code == 204

    listed = await client.get("/api/v1/usuarios", headers=headers)
    soft_deleted = next(item for item in listed.json() if item["id_usuario"] == employee["id_usuario"])
    assert soft_deleted["estado"] is False


async def test_employee_password_validation(client, auth_headers):
    response = await client.post("/api/v1/usuarios", json={
        "nombres": "Pedro",
        "apellidos": "Corto",
        "correo": "pedro@gmail.com",
        "contraseña": "123",
        "roles": ["Mesero"],
    }, headers=auth_headers["administrador"])
    assert response.status_code == 422
