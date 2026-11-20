"""Modelos de usuarios y roles."""
from sqlalchemy import Boolean, ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

usuario_rol = Table("usuario_rol", Base.metadata,
    Column("id_usuario", ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True),
    Column("id_rol", ForeignKey("roles.id_rol", ondelete="CASCADE"), primary_key=True))


class Rol(Base):
    """Rol RBAC."""
    __tablename__ = "roles"
    id_rol: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    descripcion: Mapped[str] = mapped_column(String(255), default="")


class Usuario(Base):
    """Usuario del sistema."""
    __tablename__ = "usuarios"
    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    nombres: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hash_contraseña: Mapped[str] = mapped_column("hash_contrasena", String(255))
    estado: Mapped[bool] = mapped_column(Boolean, default=True)
    roles: Mapped[list[Rol]] = relationship(secondary=usuario_rol, lazy="selectin")
