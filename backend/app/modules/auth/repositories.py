"""Acceso a credenciales y auditoría de sesiones."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.auth.models import SessionToken
from app.modules.usuarios.models import Usuario


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.email == email))

    def create_session(
        self,
        *,
        user: Usuario,
        jti: str,
        issued_at: datetime,
        expires_at: datetime,
        user_agent: str | None,
    ) -> SessionToken:
        user.ultimo_ingreso_en = issued_at
        session_token = SessionToken(
            user_id=user.id,
            jti=jti,
            issued_at=issued_at,
            expires_at=expires_at,
            user_agent=user_agent,
        )
        self.db.add(user)
        self.db.add(session_token)
        self.db.commit()
        self.db.refresh(session_token)
        return session_token

    def get_active_session(self, jti: str, user_id: int, now: datetime) -> SessionToken | None:
        return self.db.scalar(
            select(SessionToken).where(
                SessionToken.jti == jti,
                SessionToken.user_id == user_id,
                SessionToken.revoked_at.is_(None),
                SessionToken.expires_at > now,
            )
        )

    def revoke_session(self, jti: str, revoked_at: datetime) -> None:
        self.db.execute(
            update(SessionToken)
            .where(SessionToken.jti == jti, SessionToken.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        self.db.commit()
