"""Modelo relacional de las mesas del restaurante."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Mesa(Base):
    __tablename__ = "mesa"
    __table_args__ = (
        CheckConstraint("capacidad > 0", name="ck_mesa_capacidad_positiva"),
        CheckConstraint("estado IN ('LIBRE', 'OCUPADA', 'INACTIVA')", name="ck_mesa_estado"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    zona: Mapped[str | None] = mapped_column(String(80))
    capacidad: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="LIBRE", server_default="LIBRE")
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
