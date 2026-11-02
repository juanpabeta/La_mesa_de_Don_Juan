"""Dependencias FastAPI para base de datos, sesión autenticada y autorización."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.modules.auth.repositories import AuthRepository
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.repositories import UsuarioRepository

DatabaseSession = Annotated[Session, Depends(get_db)]


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Usuario:
    token = request.cookies.get(settings.auth_cookie_name)
    if not token:
        authorization = request.headers.get("Authorization", "")
        scheme, separator, credentials = authorization.partition(" ")
        if separator and scheme.lower() == "bearer":
            token = credentials.strip()
    if not token:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    try:
        payload = decode_access_token(token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada") from exc
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada") from exc
    session_token = AuthRepository(db).get_active_session(
        str(payload["jti"]), user_id, datetime.now(UTC)
    )
    if session_token is None:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    user = UsuarioRepository(db).get_by_id(user_id)
    if user is None or not user.activo:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    return user


def require_roles(allowed_roles: list[str] | str, *additional_roles: str) -> Callable:
    requested_roles = [allowed_roles] if isinstance(allowed_roles, str) else list(allowed_roles)
    requested_roles.extend(additional_roles)
    aliases = {"ADMINISTRADOR": "ADMIN"}
    normalized_roles = {aliases.get(role.strip().upper(), role.strip().upper()) for role in requested_roles}

    def role_dependency(user: Usuario = Depends(get_current_user)) -> Usuario:
        user_roles = {
            aliases.get(role.nombre.strip().upper(), role.nombre.strip().upper()) for role in user.roles
        }
        if not normalized_roles.intersection(user_roles):
            raise HTTPException(
                status_code=403,
                detail="No tiene permisos suficientes para realizar esta acción",
            )
        return user

    return role_dependency
