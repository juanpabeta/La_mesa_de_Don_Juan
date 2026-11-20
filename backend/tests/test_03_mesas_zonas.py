from sqlalchemy import select

from app.modules.mesas.models import Mesa


async def test_create_filter_update_and_soft_delete_table(client, auth_headers, session_factory):
    headers = auth_headers["administrador"]
    response = await client.post("/api/v1/mesas", json={
        "numero_mesa": 101,
        "zona": "Terraza",
        "capacidad": 4,
    }, headers=headers)
    assert response.status_code == 200
    mesa = response.json()
    assert mesa["estado"] == "Disponible"

    filtered = await client.get("/api/v1/mesas", params={"zona": "Terraza"}, headers=headers)
    assert [item["id_mesa"] for item in filtered.json()].count(mesa["id_mesa"]) == 1

    updated = await client.patch(f"/api/v1/mesas/{mesa['id_mesa']}", json={"capacidad": 6}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["capacidad"] == 6

    deleted = await client.delete(f"/api/v1/mesas/{mesa['id_mesa']}", headers=headers)
    assert deleted.status_code == 204
    filtered_after_delete = await client.get("/api/v1/mesas", headers=headers)
    assert mesa["id_mesa"] not in [item["id_mesa"] for item in filtered_after_delete.json()]

    async with session_factory() as db:
        persisted = await db.get(Mesa, mesa["id_mesa"])
        assert persisted is not None
        assert persisted.activa is False


async def test_duplicate_and_invalid_table_values(client, auth_headers):
    headers = auth_headers["administrador"]
    base = {"numero_mesa": 102, "zona": "Salón", "capacidad": 4}
    assert (await client.post("/api/v1/mesas", json=base, headers=headers)).status_code == 200
    assert (await client.post("/api/v1/mesas", json=base, headers=headers)).status_code == 409
    assert (await client.post("/api/v1/mesas", json={"numero_mesa": 0, "zona": "Salón", "capacidad": 4}, headers=headers)).status_code == 422
    assert (await client.post("/api/v1/mesas", json={"numero_mesa": 103, "zona": "Salón", "capacidad": 0}, headers=headers)).status_code == 422
