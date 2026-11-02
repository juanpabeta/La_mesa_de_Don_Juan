"""Modelo relacional de incidencias de pedidos."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IncidenciaPedido(Base):
    __tablename__ = "incidencia_pedido"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pedido_id: Mapped[int | None] = mapped_column(ForeignKey("pedido.id", ondelete="SET NULL"), index=True)
    registrada_por_id: Mapped[int] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resuelta_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    eliminada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    eliminada_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id", ondelete="RESTRICT", name="fk_incidencia_eliminada_por_usuario")
    )
