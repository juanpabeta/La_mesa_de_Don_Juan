"""Consultas ORM auditables para incidencias."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.incidencias.models import IncidenciaPedido


class IncidenciaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, incidencia: IncidenciaPedido) -> IncidenciaPedido:
        self.db.add(incidencia)
        self.db.commit()
        self.db.refresh(incidencia)
        return incidencia

    def list(self, *, desde: datetime | None = None, hasta: datetime | None = None) -> list[IncidenciaPedido]:
        statement = select(IncidenciaPedido)
        statement = statement.where(IncidenciaPedido.eliminada_en.is_(None))
        if desde is not None:
            statement = statement.where(IncidenciaPedido.creada_en >= desde)
        if hasta is not None:
            statement = statement.where(IncidenciaPedido.creada_en < hasta)
        return list(self.db.scalars(statement.order_by(IncidenciaPedido.creada_en.desc())))

    def mark_deleted(self, incidencia: IncidenciaPedido, *, deleted_by_id: int, deleted_at: datetime) -> None:
        incidencia.eliminada_por_id = deleted_by_id
        incidencia.eliminada_en = deleted_at
        self.db.add(incidencia)
        self.db.commit()

    def get_by_id(self, incidencia_id: int) -> IncidenciaPedido | None:
        return self.db.scalar(
            select(IncidenciaPedido).where(
                IncidenciaPedido.id == incidencia_id,
                IncidenciaPedido.eliminada_en.is_(None),
            )
        )
