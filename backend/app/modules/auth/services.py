"""Reglas de negocio de inicio y cierre de sesión."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, decode_access_token, verify_password
from app.modules.auth.repositories import AuthRepository
from app.modules.usuarios.models import Usuario


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def login(self, *, email: str, password: str, user_agent: str | None) -> tuple[str, datetime]:
        user = self.repository.get_user_by_email(email.strip().lower())
        if user is None or not user.activo or not verify_password(password, user.password_hash):
            raise AuthenticationError("Correo o contraseña incorrectos")
        now = datetime.now(UTC)
        expires_delta = timedelta(minutes=settings.access_token_minutes)
        jti = uuid4().hex
        expires_at = now + expires_delta
        token = create_access_token(
            {"sub": str(user.id), "roles": [role.nombre for role in user.roles], "jti": jti},
            expires_delta=expires_delta,
        )
        self.repository.create_session(
            user=user,
            jti=jti,
            issued_at=now,
            expires_at=expires_at,
            user_agent=user_agent[:512] if user_agent else None,
        )
        return token, expires_at

    def logout(self, token: str | None) -> None:
        if not token:
            return
        try:
            payload = decode_access_token(token)
        except AuthenticationError:
            return
        self.repository.revoke_session(str(payload["jti"]), datetime.now(UTC))

    @staticmethod
    def to_user_session(user: Usuario) -> dict[str, object]:
        return {
            "id": user.id,
            "nombre_completo": user.nombre_completo,
            "email": user.email,
            "roles": [role.nombre for role in user.roles],
        }
