"""Fixtures aisladas para probar la API sin conectarse al PostgreSQL del usuario."""

import os
import sys
from pathlib import Path

os.environ["APP_ENV"] = "test"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import password_context
from app.main import app
from app.modules.usuarios.models import Rol, Usuario

TEST_PASSWORD = "Mesasync-test-password-123!"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(connection, _record) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    return sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session")
def test_password_hash() -> str:
    # bcrypt se conserva en las pruebas; solo se reduce su costo para no ralentizar toda la suite.
    return password_context.handler("bcrypt").using(rounds=4).hash(TEST_PASSWORD)


@pytest.fixture(autouse=True)
def clean_database(test_engine) -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(test_session_factory) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        with test_session_factory() as db:
            yield db

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app, base_url="https://testserver") as test_client:
            yield test_client
    finally:
        app.dependency_overrides = original_overrides


@pytest.fixture
def seeded_users(test_session_factory, test_password_hash: str) -> dict[str, dict[str, int | str]]:
    roles = {name: Rol(nombre=name, descripcion=name.title()) for name in ("ADMIN", "GERENTE", "MESERO", "COCINA")}
    users = {
        "admin": Usuario(
            nombre_completo="Administradora de Prueba",
            email="admin@example.com",
            password_hash=test_password_hash,
            roles=[roles["ADMIN"]],
        ),
        "mesero": Usuario(
            nombre_completo="Mesero de Prueba",
            email="mesero@example.com",
            password_hash=test_password_hash,
            roles=[roles["MESERO"]],
        ),
        "cocina": Usuario(
            nombre_completo="Cocina de Prueba",
            email="cocina@example.com",
            password_hash=test_password_hash,
            roles=[roles["COCINA"]],
        ),
    }
    with test_session_factory() as db:
        db.add_all(roles.values())
        db.add_all(users.values())
        db.commit()
        return {
            name: {"id": user.id, "email": user.email, "password": TEST_PASSWORD}
            for name, user in users.items()
        }


@pytest.fixture
def admin_client(client: TestClient, seeded_users: dict[str, dict[str, int | str]]) -> TestClient:
    response = client.post(
        "/api/v1/auth/login",
        json={"correo": seeded_users["admin"]["email"], "contrasena": TEST_PASSWORD},
    )
    assert response.status_code == 200
    return client
