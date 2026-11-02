"""Reglas de pedidos: disponibilidad, máquina de estados y tickets de cocina."""

from datetime import UTC, datetime

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.modules.menu.repositories import PlatoRepository
from app.modules.mesas.repositories import MesaRepository
from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.pedidos.repositories import PedidoRepository

ACTIVE_STATES = ("PENDIENTE", "EN_PREPARACION", "LISTO")
ALLOWED_TRANSITIONS = {
    "PENDIENTE": {"EN_PREPARACION", "CANCELADO"},
    "EN_PREPARACION": {"LISTO", "CANCELADO"},
    "LISTO": {"ENTREGADO", "CANCELADO"},
    "ENTREGADO": set(),
    "CANCELADO": set(),
}


class PedidoService:
    def __init__(self, repository: PedidoRepository, mesas: MesaRepository, platos: PlatoRepository):
        self.repository = repository
        self.mesas = mesas
        self.platos = platos

    def create_order(self, *, mesa_id: int, creado_por_id: int, detalles: list[dict[str, object]], notas: str | None) -> Pedido:
        mesa = self.mesas.get_by_id(mesa_id)
        if mesa is None:
            raise NotFoundError("No se encontró la mesa")
        if mesa.estado != "LIBRE":
            raise ConflictError("La mesa no está disponible")
        requested_ids = [int(item["plato_id"]) for item in detalles]
        dishes = {dish.id: dish for dish in self.platos.get_by_ids(requested_ids)}
        if len(dishes) != len(set(requested_ids)):
            raise BusinessRuleError("Uno o más platos no existen")
        if any(not dishes[dish_id].disponible for dish_id in requested_ids):
            raise BusinessRuleError("La comanda contiene platos que no están disponibles")

        order = Pedido(mesa_id=mesa_id, creado_por_id=creado_por_id, estado="PENDIENTE", notas=notas)
        order.detalles = [
            DetallePedido(
                plato_id=dishes[int(item["plato_id"])].id,
                nombre_plato=dishes[int(item["plato_id"])].nombre,
                cantidad=int(item["cantidad"]),
                precio_unitario=dishes[int(item["plato_id"])].precio,
                tiempo_preparacion_minutos=dishes[int(item["plato_id"])].tiempo_preparacion_minutos,
                notas=item.get("notas"),
            )
            for item in detalles
        ]
        created = self.repository.create_if_table_available(order)
        if created is None:
            raise ConflictError("La mesa dejó de estar disponible al registrar la comanda")
        return created

    def list_ticket_orders(self) -> list[dict[str, object]]:
        now = datetime.now(UTC)
        orders = self.repository.list_for_tickets(ACTIVE_STATES)
        self._mark_delayed_orders(orders, now)
        result: list[dict[str, object]] = []
        for order in orders:
            start = self._as_utc(order.inicio_preparacion_en or order.creado_en)
            estimate = max((line.tiempo_preparacion_minutos for line in order.detalles), default=1)
            elapsed = max(0, int((now - start).total_seconds() // 60))
            result.append(
                {
                    "id": order.id,
                    "mesa_id": order.mesa_id,
                    "creado_por_id": order.creado_por_id,
                    "estado": order.estado,
                    "creado_en": order.creado_en,
                    "inicio_preparacion_en": order.inicio_preparacion_en,
                    "listo_en": order.listo_en,
                    "entregado_en": order.entregado_en,
                    "cancelado_en": order.cancelado_en,
                    "retrasado": order.retrasado,
                    "retraso_marcado_en": order.retraso_marcado_en,
                    "notas": order.notas,
                    "detalles": order.detalles,
                    "numero_mesa": order.mesa.numero,
                    "minutos_estimados": estimate,
                    "minutos_transcurridos": elapsed,
                }
            )
        return result

    def get_order(self, pedido_id: int) -> Pedido:
        order = self.repository.get_by_id(pedido_id)
        if order is None:
            raise NotFoundError("No se encontró el pedido")
        return order

    def mark_overdue_orders(self) -> int:
        """Marca pedidos vencidos periódicamente, aunque no se consulte el tablero."""
        now = datetime.now(UTC)
        orders = self.repository.list_for_tickets(ACTIVE_STATES)
        return self._mark_delayed_orders(orders, now)

    def _mark_delayed_orders(self, orders: list[Pedido], now: datetime) -> int:
        overdue: list[Pedido] = []
        for order in orders:
            if order.retrasado:
                continue
            start = self._as_utc(order.inicio_preparacion_en or order.creado_en)
            estimate = max((line.tiempo_preparacion_minutos for line in order.detalles), default=1)
            elapsed = max(0, int((now - start).total_seconds() // 60))
            if elapsed > estimate:
                overdue.append(order)
        if not overdue:
            return 0

        marked_at = now
        updated_count = self.repository.mark_delayed(
            [order.id for order in overdue], ACTIVE_STATES, marked_at
        )
        for order in overdue:
            order.retrasado = True
            order.retraso_marcado_en = marked_at
        return updated_count

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def change_status(self, pedido_id: int, estado: str) -> Pedido:
        order = self.repository.get_by_id(pedido_id)
        if order is None:
            raise NotFoundError("No se encontró el pedido")
        if estado not in ALLOWED_TRANSITIONS.get(order.estado, set()):
            raise BusinessRuleError(f"No se permite cambiar el pedido de {order.estado} a {estado}")
        now = datetime.now(UTC)
        order.estado = estado
        if estado == "EN_PREPARACION":
            order.inicio_preparacion_en = now
        elif estado == "LISTO":
            order.listo_en = now
        elif estado == "ENTREGADO":
            order.entregado_en = now
        elif estado == "CANCELADO":
            order.cancelado_en = now
        saved = self.repository.save(order)
        if estado in {"ENTREGADO", "CANCELADO"} and not self.repository.has_active_for_table(saved.mesa_id, ACTIVE_STATES):
            self.mesas.set_free_if_occupied(saved.mesa_id)
        return saved

    def delete_order(self, pedido_id: int, *, deleted_by_id: int) -> None:
        order = self.repository.get_by_id(pedido_id)
        if order is None:
            raise NotFoundError("No se encontró el pedido")
        if order.estado in ACTIVE_STATES:
            raise BusinessRuleError("Un pedido activo debe cancelarse mediante su cambio de estado")
        mesa_id = order.mesa_id
        self.repository.mark_deleted(order, deleted_by_id=deleted_by_id, deleted_at=datetime.now(UTC))
        if not self.repository.has_active_for_table(mesa_id, ACTIVE_STATES):
            self.mesas.set_free_if_occupied(mesa_id)
