"""Modelo relacional de platos disponibles para las comandas."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Plato(Base):
    __tablename__ = "plato"
    __table_args__ = (
        CheckConstraint("precio >= 0", name="ck_plato_precio_no_negativo"),
        CheckConstraint("tiempo_preparacion_minutos > 0", name="ck_plato_tiempo_positivo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria: Mapped[str | None] = mapped_column(String(80), index=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tiempo_preparacion_minutos: Mapped[int] = mapped_column(Integer, nullable=False, default=15, server_default="15")
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true", index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
