"""Consultas SQL analíticas para tiempos e incidencias."""

from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.incidencias.models import IncidenciaPedido
from app.modules.pedidos.models import Pedido


class ReporteRepository:
    def __init__(self, db: Session):
        self.db = db

    def completed_order_durations(self, desde: date, hasta: date) -> tuple[int, float | None, float | None]:
        start = datetime.combine(desde, time.min, tzinfo=timezone.utc)
        end = datetime.combine(hasta + timedelta(days=1), time.min, tzinfo=timezone.utc)
        duration_seconds = func.extract("epoch", Pedido.entregado_en - Pedido.creado_en)
        row = self.db.execute(
            select(func.count(Pedido.id), func.avg(duration_seconds), func.max(duration_seconds)).where(
                Pedido.estado == "ENTREGADO",
                Pedido.eliminado_en.is_(None),
                Pedido.entregado_en >= start,
                Pedido.entregado_en < end,
            )
        ).one()
        return (
            int(row[0] or 0),
            float(row[1]) if row[1] is not None else None,
            float(row[2]) if row[2] is not None else None,
        )

    def list_incidents(self, desde: date | None, hasta: date | None) -> list[IncidenciaPedido]:
        statement = select(IncidenciaPedido)
        if desde is not None:
            start = datetime.combine(desde, time.min, tzinfo=timezone.utc)
            statement = statement.where(IncidenciaPedido.creada_en >= start)
        if hasta is not None:
            end = datetime.combine(hasta + timedelta(days=1), time.min, tzinfo=timezone.utc)
            statement = statement.where(IncidenciaPedido.creada_en < end)
        return list(self.db.scalars(statement.order_by(IncidenciaPedido.creada_en).limit(10_000)))
