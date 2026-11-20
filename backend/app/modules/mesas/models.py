"""Modelo de mesas."""
from sqlalchemy import Boolean, CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Mesa(Base):
    """Mesa física del restaurante."""
    __tablename__ = "mesas"
    __table_args__ = (CheckConstraint("numero_mesa > 0"), CheckConstraint("capacidad > 0"))
    id_mesa: Mapped[int] = mapped_column(primary_key=True)
    numero_mesa: Mapped[int] = mapped_column(Integer, unique=True)
    zona: Mapped[str] = mapped_column(String(80))
    capacidad: Mapped[int] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(20), default="Disponible")
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
