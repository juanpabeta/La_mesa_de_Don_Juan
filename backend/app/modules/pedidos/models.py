"""Modelos de pedidos."""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Pedido(Base):
    """Comanda asociada a una mesa."""
    __tablename__ = "pedidos"
    id_pedido: Mapped[int] = mapped_column(primary_key=True)
    id_mesa: Mapped[int] = mapped_column(ForeignKey("mesas.id_mesa"))
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    estado: Mapped[str] = mapped_column(String(30), default="PENDIENTE")
    fecha_hora_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    fecha_hora_entrega: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    es_retrasado: Mapped[bool] = mapped_column(Boolean, default=False)
    propina: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    detalles: Mapped[list["DetallePedido"]] = relationship(cascade="all, delete-orphan", lazy="selectin")

    

class DetallePedido(Base):
    """Línea de pedido con precio congelado."""
    __tablename__ = "detalles_pedido"
    id_detalle: Mapped[int] = mapped_column(primary_key=True)
    id_pedido: Mapped[int] = mapped_column(ForeignKey("pedidos.id_pedido", ondelete="CASCADE"))
    id_plato: Mapped[int] = mapped_column(ForeignKey("platos.id_plato", ondelete="RESTRICT"))
    cantidad: Mapped[int] = mapped_column(Integer)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
