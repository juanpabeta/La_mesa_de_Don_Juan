"""Fixtures globales para la suite asíncrona de La mesa de Don Juan."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.modules.usuarios.models import Rol, Usuario


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def seed_users(session_factory) -> dict[str, Usuario]:
    roles = {
        name: Rol(nombre=name, descripcion=name)
        for name in ["Administrador", "Mesero", "Cocina", "Cocinero", "Cajero"]
    }
    async with session_factory() as db:
        db.add_all(list(roles.values()))
        await db.flush()
        users = {
            "administrador": Usuario(nombres="Admin", apellidos="Sistema", correo="admin@gmail.com", hash_contraseña=hash_password("Admin123!"), estado=True, roles=[roles["Administrador"]]),
            "mesero": Usuario(nombres="Mariana", apellidos="Gomez", correo="mesero@gmail.com", hash_contraseña=hash_password("Mesero123!"), estado=True, roles=[roles["Mesero"]]),
            "cocina": Usuario(nombres="Carlos", apellidos="Cocina", correo="cocina@gmail.com", hash_contraseña=hash_password("Cocina123!"), estado=True, roles=[roles["Cocina"]]),
            "cajero": Usuario(nombres="Laura", apellidos="Caja", correo="cajero@gmail.com", hash_contraseña=hash_password("Cajero123!"), estado=True, roles=[roles["Cajero"]]),
            "inactivo": Usuario(nombres="Usuario", apellidos="Inactivo", correo="inactivo@gmail.com", hash_contraseña=hash_password("Inactivo123!"), estado=False, roles=[roles["Mesero"]]),
        }
        db.add_all(list(users.values()))
        await db.commit()
        for user in users.values():
            await db.refresh(user)
    return users


@pytest_asyncio.fixture
async def override_db(session_factory):
    async def dependency() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = dependency
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(override_db) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


def bearer_for(user: Usuario) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {create_access_token(user.id_usuario, [role.nombre for role in user.roles])}"
    }


@pytest_asyncio.fixture
async def auth_headers(seed_users):
    return {name: bearer_for(user) for name, user in seed_users.items()}
