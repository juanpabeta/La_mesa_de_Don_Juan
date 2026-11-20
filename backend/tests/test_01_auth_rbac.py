from app.core.security import verify_password


async def test_login_cookie_httponly_and_me(client, seed_users):
    response = await client.post("/api/v1/auth/login", json={
        "correo": "admin@gmail.com",
        "contraseña": "Admin123!",
    })
    assert response.status_code == 200
    assert response.cookies.get("access_token")
    assert "httponly" in response.headers["set-cookie"].lower()
    assert response.json()["roles"] == ["Administrador"]

    me = await client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["correo"] == "admin@gmail.com"


async def test_password_hash_is_bcrypt_and_not_plaintext(seed_users):
    user = seed_users["administrador"]
    assert user.hash_contraseña != "Admin123!"
    assert user.hash_contraseña.startswith("$2")
    assert verify_password("Admin123!", user.hash_contraseña)


async def test_invalid_inactive_and_missing_credentials(client):
    invalid = await client.post("/api/v1/auth/login", json={
        "correo": "nadie@gmail.com",
        "contraseña": "Incorrecta123!",
    })
    assert invalid.status_code == 401

    inactive = await client.post("/api/v1/auth/login", json={
        "correo": "inactivo@gmail.com",
        "contraseña": "Inactivo123!",
    })
    assert inactive.status_code == 401

    missing = await client.get("/api/v1/usuarios")
    assert missing.status_code == 401


async def test_bearer_role_control(client, auth_headers):
    denied = await client.get("/api/v1/usuarios", headers=auth_headers["mesero"])
    assert denied.status_code == 403

    allowed = await client.get("/api/v1/usuarios", headers=auth_headers["administrador"])
    assert allowed.status_code == 200
