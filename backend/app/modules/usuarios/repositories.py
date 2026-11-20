"""Persistencia de usuarios."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.usuarios.models import Rol, Usuario


async def get_user(db: AsyncSession, email: str) -> Usuario | None:
    """Busca un usuario por correo."""
    return await db.scalar(select(Usuario).where(Usuario.correo == email))


async def get_role(db: AsyncSession, name: str) -> Rol | None:
    """Busca un rol por nombre."""
    return await db.scalar(select(Rol).where(Rol.nombre == name))
