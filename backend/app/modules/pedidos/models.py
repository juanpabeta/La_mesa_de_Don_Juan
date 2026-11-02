"""Modelos relacionales de pedidos y líneas de pedido."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Pedido(Base):
    __tablename__ = "pedido"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('PENDIENTE', 'EN_PREPARACION', 'LISTO', 'ENTREGADO', 'CANCELADO')",
            name="ck_pedido_estado",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mesa_id: Mapped[int] = mapped_column(ForeignKey("mesa.id", ondelete="RESTRICT"), index=True, nullable=False)
    creado_por_id: Mapped[int] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(24), nullable=False, default="PENDIENTE", server_default="PENDIENTE", index=True
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    inicio_preparacion_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    listo_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    entregado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retrasado: Mapped[bool] = mapped_column(nullable=False, default=False, server_default="false")
    retraso_marcado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    eliminado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    eliminado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id", ondelete="RESTRICT", name="fk_pedido_eliminado_por_usuario")
    )
    notas: Mapped[str | None] = mapped_column(Text)
    mesa: Mapped["Mesa"] = relationship("Mesa", lazy="joined")
    detalles: Mapped[list["DetallePedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan", lazy="selectin"
    )


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_detalle_cantidad_positiva"),
        CheckConstraint("precio_unitario >= 0", name="ck_detalle_precio_no_negativo"),
        CheckConstraint("tiempo_preparacion_minutos > 0", name="ck_detalle_tiempo_positivo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedido.id", ondelete="CASCADE"), index=True, nullable=False)
    plato_id: Mapped[int] = mapped_column(ForeignKey("plato.id", ondelete="RESTRICT"), nullable=False)
    nombre_plato: Mapped[str] = mapped_column(String(120), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tiempo_preparacion_minutos: Mapped[int] = mapped_column(Integer, nullable=False)
    notas: Mapped[str | None] = mapped_column(Text)
    pedido: Mapped[Pedido] = relationship(back_populates="detalles")
