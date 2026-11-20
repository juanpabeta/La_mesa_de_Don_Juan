from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas import LoginRequest
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.modules.usuarios.models import Usuario


class AuthService:
    """Autenticación contra usuarios persistidos."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def login(self, data: LoginRequest) -> str:
        usuario = await self.db.scalar(
            select(Usuario).where(Usuario.correo == str(data.correo))
        )
        if usuario is None or not verify_password(data.contraseña, usuario.hash_contraseña):
            raise AuthenticationError("Credenciales inválidas")
        if not usuario.estado:
            raise AuthenticationError("Usuario inactivo")

        return create_access_token(
            usuario.id_usuario,
            roles=[role.nombre for role in usuario.roles],
        )
