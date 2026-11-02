from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.modules.usuarios.models import Usuario


def login(client: TestClient, email: str, password: str) -> None:
    response = client.post("/api/v1/auth/login", json={"correo": email, "contrasena": password})
    assert response.status_code == 200


def test_login_sets_httponly_cookie_without_returning_token(client: TestClient, seeded_users) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"correo": seeded_users["admin"]["email"], "contrasena": seeded_users["admin"]["password"]},
    )

    assert response.status_code == 200
    assert "access_token" not in response.json()
    assert response.json()["token_type"] == "cookie"
    assert response.headers["cache-control"] == "no-store"
    cookie = response.headers["set-cookie"].lower()
    assert f"{settings.auth_cookie_name.lower()}=" in cookie
    assert "httponly" in cookie
    assert f"samesite={settings.cookie_samesite}" in cookie
    if settings.cookie_secure:
        assert "secure" in cookie


def test_cookie_and_bearer_authenticate_current_user(client: TestClient, seeded_users) -> None:
    login(client, seeded_users["admin"]["email"], seeded_users["admin"]["password"])
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"

    token = client.cookies.get(settings.auth_cookie_name)
    claims = decode_access_token(token)
    assert claims["sub"] == str(response.json()["id"])
    assert claims["roles"] == ["ADMIN"]
    client.cookies.clear()
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_invalid_credentials_do_not_issue_cookie(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@example.com", "contrasena": "incorrecta"},
    )
    assert response.status_code == 401
    assert "set-cookie" not in response.headers


def test_invalid_token_and_missing_authentication_are_rejected(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401
    client.cookies.set(settings.auth_cookie_name, "token-invalido")
    assert client.get("/api/v1/auth/me").status_code == 401


def test_expired_token_is_rejected(client: TestClient, seeded_users) -> None:
    token = create_access_token(
        {"sub": str(seeded_users["admin"]["id"]), "roles": ["ADMIN"]},
        expires_delta=timedelta(seconds=-1),
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_logout_revokes_cookie_session_and_bearer_session(client: TestClient, seeded_users) -> None:
    login(client, seeded_users["admin"]["email"], seeded_users["admin"]["password"])
    token = client.cookies.get(settings.auth_cookie_name)
    client.cookies.clear()

    logout = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 204
    assert "max-age=0" in logout.headers["set-cookie"].lower()
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_admin_routes_require_authentication_and_admin_role(client: TestClient, seeded_users) -> None:
    assert client.get("/api/v1/usuarios").status_code == 401

    login(client, seeded_users["mesero"]["email"], seeded_users["mesero"]["password"])
    assert client.get("/api/v1/usuarios").status_code == 403

    client.cookies.clear()
    login(client, seeded_users["admin"]["email"], seeded_users["admin"]["password"])
    assert client.get("/api/v1/usuarios").status_code == 200


def test_role_changes_apply_to_existing_session(admin_client: TestClient, seeded_users) -> None:
    response = admin_client.put(
        f"/api/v1/usuarios/{seeded_users['admin']['id']}/roles",
        json={"roles": ["MESERO"]},
    )
    assert response.status_code == 200
    assert admin_client.get("/api/v1/usuarios").status_code == 403


def test_deactivated_user_cannot_keep_using_existing_session(
    client: TestClient,
    seeded_users,
    test_session_factory: sessionmaker,
) -> None:
    login(client, seeded_users["admin"]["email"], seeded_users["admin"]["password"])
    with test_session_factory() as db:
        user = db.get(Usuario, seeded_users["admin"]["id"])
        user.activo = False
        db.commit()

    assert client.get("/api/v1/auth/me").status_code == 401
