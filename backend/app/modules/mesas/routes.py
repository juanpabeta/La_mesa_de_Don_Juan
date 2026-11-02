"""Endpoints HTTP de mesas y zonas."""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import DatabaseSession, require_roles
from app.modules.mesas.repositories import MesaRepository
from app.modules.mesas.schemas import DeleteResponse, MesaCreate, MesaResponse, MesaStatusUpdate
from app.modules.mesas.services import MesaService
from app.modules.pedidos.repositories import PedidoRepository

router = APIRouter(prefix="/mesas", tags=["Mesas"])


def get_mesa_service(db: DatabaseSession) -> MesaService:
    return MesaService(MesaRepository(db), PedidoRepository(db))


@router.get("", response_model=list[MesaResponse])
def list_tables(_actor=Depends(require_roles("ADMIN", "GERENTE", "MESERO", "COCINA")), service: MesaService = Depends(get_mesa_service)):
    return service.list_tables()


@router.post("", response_model=MesaResponse, status_code=status.HTTP_201_CREATED)
def create_table(
    payload: MesaCreate,
    _actor=Depends(require_roles("ADMIN")),
    service: MesaService = Depends(get_mesa_service),
):
    return service.create_table(numero=payload.numero, zona=payload.zona, capacidad=payload.capacidad)


@router.patch("/{mesa_id}", response_model=MesaResponse)
def update_table_status(
    mesa_id: int,
    payload: MesaStatusUpdate,
    _actor=Depends(require_roles("ADMIN")),
    service: MesaService = Depends(get_mesa_service),
):
    return service.update_status(mesa_id, payload.estado)


@router.delete("/{mesa_id}", response_model=DeleteResponse)
def delete_table(
    mesa_id: int,
    _actor=Depends(require_roles("ADMIN")),
    service: MesaService = Depends(get_mesa_service),
):
    mesa = service.delete_table(mesa_id)
    return DeleteResponse(message="Mesa marcada como inactiva", id=mesa.id)
