"""Reglas de usuarios."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password
from app.core.exceptions import BadRequestError
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.repositories import get_role, get_user
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioUpdate


async def authenticate(db: AsyncSession, email: str, password: str) -> Usuario | None:
    """Valida credenciales."""
    user = await get_user(db, email)
    return user if user and user.estado and verify_password(password, user.hash_contraseña) else None


async def create_user(db: AsyncSession, data: UsuarioCreate) -> Usuario:
    """Crea un usuario y asigna roles."""
    user = Usuario(nombres=data.nombres, apellidos=data.apellidos, correo=str(data.correo), hash_contraseña=hash_password(data.contraseña))
    for name in data.roles:
        role = await get_role(db, name)
        if role is None:
            raise BadRequestError(f"El rol '{name}' no existe")
        user.roles.append(role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: Usuario, data: UsuarioUpdate) -> Usuario:
    """Actualiza los datos y roles de un usuario."""
    values = data.model_dump(exclude_unset=True, exclude={"contraseña", "roles"})
    for field, value in values.items():
        setattr(user, field, str(value) if field == "correo" else value)

    if data.contraseña is not None:
        user.hash_contraseña = hash_password(data.contraseña)

    if data.roles is not None:
        if not data.roles:
            raise BadRequestError("El usuario debe tener al menos un rol")
        user.roles.clear()
        for name in data.roles:
            role = await get_role(db, name)
            if role is None:
                raise BadRequestError(f"El rol '{name}' no existe")
            user.roles.append(role)

    await db.commit()
    await db.refresh(user)
    return user
