"""Modelo de incidencias."""
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class IncidenciaPedido(Base):
    """Registro auditable de una incidencia."""
    __tablename__ = "incidencias_pedido"
    id_incidencia: Mapped[int] = mapped_column(primary_key=True)
    id_pedido: Mapped[int] = mapped_column(ForeignKey("pedidos.id_pedido"))
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    tipo_error: Mapped[str] = mapped_column(String(80))
    descripcion: Mapped[str] = mapped_column(Text)
    prioridad: Mapped[str] = mapped_column(String(20), default="MEDIA")
    estado: Mapped[str] = mapped_column(String(20), default="ABIERTA")
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
