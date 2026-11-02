"""Consultas ORM para empleados y asignación de roles."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.usuarios.models import Rol, Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Usuario]:
        return list(self.db.scalars(select(Usuario).options(selectinload(Usuario.roles)).order_by(Usuario.id).limit(1_000)))

    def get_by_id(self, user_id: int) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.id == user_id).options(selectinload(Usuario.roles)))

    def email_exists(self, email: str, exclude_id: int | None = None) -> bool:
        statement = select(Usuario.id).where(Usuario.email == email)
        if exclude_id is not None:
            statement = statement.where(Usuario.id != exclude_id)
        return self.db.scalar(statement) is not None

    def get_roles_by_names(self, names: list[str]) -> list[Rol]:
        return list(self.db.scalars(select(Rol).where(Rol.nombre.in_(names))))

    def create(self, *, nombre_completo: str, email: str, password_hash: str, roles: list[Rol]) -> Usuario:
        usuario = Usuario(nombre_completo=nombre_completo, email=email, password_hash=password_hash, roles=roles)
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update(self, usuario: Usuario, changes: dict[str, object]) -> Usuario:
        for field, value in changes.items():
            setattr(usuario, field, value)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update_roles(self, usuario: Usuario, roles: list[Rol]) -> Usuario:
        usuario.roles = roles
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def deactivate(self, usuario: Usuario) -> Usuario:
        usuario.activo = False
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
