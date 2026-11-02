"""Reglas de negocio sobre capacidad y disponibilidad de mesas."""

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.modules.mesas.models import Mesa
from app.modules.mesas.repositories import MesaRepository
from app.modules.pedidos.repositories import PedidoRepository


class MesaService:
    def __init__(self, repository: MesaRepository, pedidos: PedidoRepository):
        self.repository = repository
        self.pedidos = pedidos

    def list_tables(self) -> list[Mesa]:
        return self.repository.list()

    def create_table(self, *, numero: int, zona: str | None, capacidad: int) -> Mesa:
        if numero <= 0 or capacidad <= 0:
            raise BusinessRuleError("El número y la capacidad de la mesa deben ser positivos")
        if self.repository.get_by_number(numero) is not None:
            raise ConflictError("Ya existe una mesa con ese número")
        return self.repository.create(Mesa(numero=numero, zona=zona, capacidad=capacidad))

    def update_status(self, mesa_id: int, estado: str) -> Mesa:
        mesa = self.repository.get_by_id(mesa_id)
        if mesa is None:
            raise NotFoundError("No se encontró la mesa")
        if estado not in {"LIBRE", "INACTIVA"}:
            raise BusinessRuleError("El estado solo puede ser LIBRE o INACTIVA desde esta operación")
        if self.pedidos.has_active_for_table(mesa_id, ("PENDIENTE", "EN_PREPARACION", "LISTO")):
            raise ConflictError("No se puede cambiar una mesa con un pedido activo")
        return self.repository.update_status(mesa, estado)

    def delete_table(self, mesa_id: int) -> Mesa:
        mesa = self.repository.get_by_id(mesa_id)
        if mesa is None:
            raise NotFoundError("No se encontró la mesa")
        if mesa.estado == "OCUPADA" or self.pedidos.has_active_for_table(mesa_id, ("PENDIENTE", "EN_PREPARACION", "LISTO")):
            raise ConflictError("No se puede eliminar una mesa con un pedido activo")
        return self.repository.deactivate(mesa)
