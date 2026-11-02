"""Modelos relacionales de usuarios y roles del restaurante."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    ultimo_ingreso_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    roles: Mapped[list["Rol"]] = relationship("Rol", secondary="usuario_rol", back_populates="usuarios")


class Rol(Base):
    __tablename__ = "rol"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    usuarios: Mapped[list[Usuario]] = relationship("Usuario", secondary="usuario_rol", back_populates="roles")


class UsuarioRol(Base):
    __tablename__ = "usuario_rol"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True)
    rol_id: Mapped[int] = mapped_column(ForeignKey("rol.id", ondelete="CASCADE"), primary_key=True)
