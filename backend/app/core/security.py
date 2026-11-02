"""Hash de contraseñas y emisión/verificación de JWT."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AuthenticationError

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def hash_password(password: str) -> str:
    """Alias de compatibilidad para servicios existentes."""
    return get_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    now = datetime.now(UTC)
    lifetime = expires_delta or timedelta(minutes=settings.access_token_minutes)
    payload = data.copy()
    payload.setdefault("iat", now)
    payload.setdefault("jti", uuid4().hex)
    payload.setdefault("token_type", "access")
    payload["exp"] = now + lifetime
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "sub", "jti", "roles", "token_type"]},
        )
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("La sesión no es válida o ha expirado") from exc
    if not isinstance(payload, dict):
        raise AuthenticationError("La sesión no contiene un objeto de claims válido")
    subject = payload.get("sub")
    token_id = payload.get("jti")
    roles = payload.get("roles")
    if (
        not isinstance(subject, str)
        or not subject.isdecimal()
        or len(subject) > 10
        or int(subject) < 1
        or int(subject) > 2_147_483_647
        or not isinstance(token_id, str)
        or not token_id
        or len(token_id) > 64
        or payload.get("token_type") != "access"
        or not isinstance(roles, list)
        or any(not isinstance(role, str) or not role.strip() for role in roles)
    ):
        raise AuthenticationError("La sesión no contiene los datos requeridos")
    return payload
