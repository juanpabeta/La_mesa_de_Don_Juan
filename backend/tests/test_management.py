from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.mesas.models import Mesa
from app.modules.menu.models import Plato
from app.modules.usuarios.models import Usuario


def test_admin_can_create_and_deactivate_menu_and_table(admin_client: TestClient, test_session_factory: sessionmaker) -> None:
    table_response = admin_client.post(
        "/api/v1/mesas",
        json={"numero": 12, "zona": "Terraza", "capacidad": 4},
    )
    assert table_response.status_code == 201
    table_id = table_response.json()["id"]

    dish_response = admin_client.post(
        "/api/v1/menu",
        json={
            "nombre": "Arepa de prueba",
            "categoria": "Entradas",
            "precio": "12.50",
            "tiempo_preparacion_minutos": 8,
        },
    )
    assert dish_response.status_code == 201
    dish_id = dish_response.json()["id"]

    assert admin_client.delete(f"/api/v1/menu/{dish_id}").status_code == 200
    assert admin_client.get("/api/v1/menu").json() == []
    assert admin_client.delete(f"/api/v1/mesas/{table_id}").status_code == 200

    with test_session_factory() as db:
        assert db.get(Plato, dish_id).disponible is False
        assert db.get(Mesa, table_id).estado == "INACTIVA"


def test_non_admin_cannot_create_menu_or_tables(client: TestClient, seeded_users) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"correo": seeded_users["mesero"]["email"], "contrasena": seeded_users["mesero"]["password"]},
    )
    assert response.status_code == 200
    assert client.post("/api/v1/mesas", json={"numero": 1, "capacidad": 2}).status_code == 403
    assert client.post(
        "/api/v1/menu",
        json={"nombre": "Plato no autorizado", "precio": "10.00"},
    ).status_code == 403


def test_user_creation_hashes_password_and_delete_deactivates_user(
    admin_client: TestClient,
    test_session_factory: sessionmaker,
) -> None:
    created = admin_client.post(
        "/api/v1/usuarios",
        json={
            "nombre_completo": "Personal Nuevo",
            "email": "nuevo@example.com",
            "password": "new-secure-password-123",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]
    assert "password_hash" not in created.json()
    assert [role["nombre"] for role in created.json()["roles"]] == ["MESERO"]

    deleted = admin_client.delete(f"/api/v1/usuarios/{user_id}")
    assert deleted.status_code == 200
    with test_session_factory() as db:
        user = db.get(Usuario, user_id)
        assert user is not None
        assert user.activo is False
