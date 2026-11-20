"""Modelo de platos."""
from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Plato(Base):
    """Plato vendible."""
    __tablename__ = "platos"
    __table_args__ = (CheckConstraint("precio > 0"), CheckConstraint("tiempo_estimado_min > 0"))
    id_plato: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    categoria: Mapped[str] = mapped_column(String(80))
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    tiempo_estimado_min: Mapped[int] = mapped_column(Integer)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    agotado: Mapped[bool] = mapped_column(Boolean, default=False)
