"""Configuración de Alembic."""
import asyncio
import sys
from pathlib import Path

# Permite importar ``app`` aunque Alembic se ejecute desde otra carpeta.
backend_dir = str(Path(__file__).resolve().parents[1])
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from alembic import context
from app.core.database import Base
from app.core.config import get_settings
from app.modules.usuarios.models import *
from app.modules.mesas.models import *
from app.modules.menu.models import *
from app.modules.pedidos.models import *
from app.modules.incidencias.models import *

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera SQL sin conectar."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Ejecuta las migraciones dentro de una conexión síncrona adaptada."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Ejecuta migraciones usando el driver asíncrono de PostgreSQL."""
    from sqlalchemy.ext.asyncio import async_engine_from_config
    from sqlalchemy import pool

    configuration = {"sqlalchemy.url": get_settings().database_url}
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Inicia las migraciones asíncronas."""
    asyncio.run(run_async_migrations())


(run_migrations_offline if context.is_offline_mode() else run_migrations_online)()
