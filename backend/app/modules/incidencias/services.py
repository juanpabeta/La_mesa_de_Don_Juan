"""Reglas de negocio para registro auditable de incidencias."""

from datetime import UTC, datetime, time, timedelta, timezone

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.incidencias.models import IncidenciaPedido
from app.modules.incidencias.repositories import IncidenciaRepository
from app.modules.pedidos.repositories import PedidoRepository


class IncidenciaService:
    def __init__(self, repository: IncidenciaRepository, pedidos: PedidoRepository):
        self.repository = repository
        self.pedidos = pedidos

    def create_incident(
        self, *, pedido_id: int | None, registrada_por_id: int, tipo: str, descripcion: str
    ) -> IncidenciaPedido:
        order = self.pedidos.get_by_id(pedido_id) if pedido_id is not None else None
        if pedido_id is not None and order is None:
            raise NotFoundError("No se encontró el pedido asociado")
        if tipo == "DEMORA" and (order is None or not order.retrasado):
            raise BusinessRuleError("Solo se puede registrar una demora para un pedido marcado como retrasado")
        if tipo == "CANCELACION" and (order is None or order.estado != "CANCELADO"):
            raise BusinessRuleError("La incidencia de cancelación requiere un pedido cancelado")
        if tipo == "MESA_EQUIVOCADA" and order is None:
            raise BusinessRuleError("La incidencia de mesa equivocada requiere un pedido asociado")
        incident = IncidenciaPedido(
            pedido_id=pedido_id,
            registrada_por_id=registrada_por_id,
            tipo=tipo,
            descripcion=descripcion.strip(),
        )
        return self.repository.create(incident)

    def list_incidents(self, desde=None, hasta=None) -> list[IncidenciaPedido]:
        if desde is not None and hasta is not None and desde > hasta:
            raise BusinessRuleError("La fecha inicial no puede ser posterior a la fecha final")
        start = datetime.combine(desde, time.min, tzinfo=timezone.utc) if desde is not None else None
        end = (
            datetime.combine(hasta + timedelta(days=1), time.min, tzinfo=timezone.utc)
            if hasta is not None
            else None
        )
        return self.repository.list(
            desde=start,
            hasta=end,
        )

    def delete_incident(self, incidencia_id: int, *, deleted_by_id: int) -> None:
        incident = self.repository.get_by_id(incidencia_id)
        if incident is None:
            raise NotFoundError("No se encontró la incidencia")
        self.repository.mark_deleted(incident, deleted_by_id=deleted_by_id, deleted_at=datetime.now(UTC))
