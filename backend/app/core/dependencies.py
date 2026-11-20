"""Dependencias de autenticación y autorización."""
from collections.abc import Callable
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.modules.usuarios.models import Usuario

bearer_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuth")

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Autentica desde Bearer (Swagger) o desde la cookie HttpOnly."""
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (AuthenticationError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user = await db.scalar(select(Usuario).where(Usuario.id_usuario == user_id, Usuario.estado.is_(True)))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(allowed_roles: list[str]) -> Callable:
    """Crea una dependencia que valida al menos uno de los roles."""
    async def checker(user: Usuario = Depends(get_current_user)) -> Usuario:
        names = {role.nombre for role in user.roles}
        if not names.intersection(allowed_roles):
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return user
    return checker
