"""Endpoints HTTP de comandas y tickets de cocina."""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import DatabaseSession, require_roles
from app.modules.menu.repositories import PlatoRepository
from app.modules.mesas.repositories import MesaRepository
from app.modules.pedidos.repositories import PedidoRepository
from app.modules.pedidos.schemas import (
    CambiarEstadoDTO,
    DeleteResponse,
    PedidoCreate,
    PedidoResponse,
    TicketPedidoResponse,
)
from app.modules.pedidos.services import PedidoService
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


def get_pedido_service(db: DatabaseSession) -> PedidoService:
    return PedidoService(PedidoRepository(db), MesaRepository(db), PlatoRepository(db))


@router.post("", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: PedidoCreate,
    actor: Usuario = Depends(require_roles("ADMIN")),
    service: PedidoService = Depends(get_pedido_service),
):
    return service.create_order(
        mesa_id=payload.mesa_id,
        creado_por_id=actor.id,
        detalles=[item.model_dump() for item in payload.detalles],
        notas=payload.notas,
    )


@router.delete("/{pedido_id}", response_model=DeleteResponse)
def delete_order(
    pedido_id: int,
    actor: Usuario = Depends(require_roles("ADMIN")),
    service: PedidoService = Depends(get_pedido_service),
):
    service.delete_order(pedido_id, deleted_by_id=actor.id)
    return DeleteResponse(message="Pedido retirado de la operación y conservado en auditoría", id=pedido_id)


@router.get("/tickets", response_model=list[TicketPedidoResponse])
def list_ticket_orders(
    _actor: Usuario = Depends(require_roles("ADMIN", "GERENTE", "COCINA")),
    service: PedidoService = Depends(get_pedido_service),
):
    return service.list_ticket_orders()


@router.get("/{pedido_id}", response_model=PedidoResponse)
def get_order(
    pedido_id: int,
    _actor: Usuario = Depends(require_roles("ADMIN", "GERENTE", "MESERO", "COCINA")),
    service: PedidoService = Depends(get_pedido_service),
):
    return service.get_order(pedido_id)


@router.patch("/{pedido_id}/estado", response_model=PedidoResponse)
def change_order_status(
    pedido_id: int,
    payload: CambiarEstadoDTO,
    _actor: Usuario = Depends(require_roles("ADMIN", "GERENTE", "COCINA")),
    service: PedidoService = Depends(get_pedido_service),
):
    return service.change_status(pedido_id, payload.estado)
