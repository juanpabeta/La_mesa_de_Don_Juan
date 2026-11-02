"""Endpoints HTTP para registro y consulta de incidencias."""

from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import DatabaseSession, require_roles
from app.modules.incidencias.repositories import IncidenciaRepository
from app.modules.incidencias.schemas import DeleteResponse, IncidenciaCreate, IncidenciaResponse
from app.modules.incidencias.services import IncidenciaService
from app.modules.pedidos.repositories import PedidoRepository
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/incidencias", tags=["Incidencias"])


def get_incidencia_service(db: DatabaseSession) -> IncidenciaService:
    return IncidenciaService(IncidenciaRepository(db), PedidoRepository(db))


@router.post("", response_model=IncidenciaResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidenciaCreate,
    actor: Usuario = Depends(require_roles("ADMIN")),
    service: IncidenciaService = Depends(get_incidencia_service),
):
    return service.create_incident(
        pedido_id=payload.pedido_id,
        registrada_por_id=actor.id,
        tipo=payload.tipo,
        descripcion=payload.descripcion,
    )


@router.get("", response_model=list[IncidenciaResponse])
def list_incidents(
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    _actor: Usuario = Depends(require_roles("ADMIN", "GERENTE")),
    service: IncidenciaService = Depends(get_incidencia_service),
):
    return service.list_incidents(desde=desde, hasta=hasta)


@router.delete("/{incidencia_id}", response_model=DeleteResponse)
def delete_incident(
    incidencia_id: int,
    actor: Usuario = Depends(require_roles("ADMIN")),
    service: IncidenciaService = Depends(get_incidencia_service),
):
    service.delete_incident(incidencia_id, deleted_by_id=actor.id)
    return DeleteResponse(message="Incidencia retirada de la consulta y conservada en auditoría", id=incidencia_id)
