"""Endpoints HTTP del catálogo comercial."""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import DatabaseSession, require_roles
from app.modules.menu.repositories import PlatoRepository
from app.modules.menu.schemas import DeleteResponse, PlatoCreate, PlatoResponse, PlatoUpdate
from app.modules.menu.services import PlatoService

router = APIRouter(prefix="/menu", tags=["Menú"])


def get_plato_service(db: DatabaseSession) -> PlatoService:
    return PlatoService(PlatoRepository(db))


@router.get("", response_model=list[PlatoResponse])
def list_dishes(
    solo_disponibles: bool = True,
    _actor=Depends(require_roles("ADMIN", "GERENTE", "MESERO", "COCINA")),
    service: PlatoService = Depends(get_plato_service),
):
    return service.list_dishes(only_available=solo_disponibles)


@router.post("", response_model=PlatoResponse, status_code=status.HTTP_201_CREATED)
def create_dish(
    payload: PlatoCreate,
    _actor=Depends(require_roles("ADMIN")),
    service: PlatoService = Depends(get_plato_service),
):
    return service.create_dish(payload.model_dump())


@router.put("/{dish_id}", response_model=PlatoResponse)
def update_dish(
    dish_id: int,
    payload: PlatoUpdate,
    _actor=Depends(require_roles("ADMIN")),
    service: PlatoService = Depends(get_plato_service),
):
    return service.update_dish(dish_id, payload.model_dump(exclude_unset=True))


@router.delete("/{dish_id}", response_model=DeleteResponse)
def delete_dish(
    dish_id: int,
    _actor=Depends(require_roles("ADMIN")),
    service: PlatoService = Depends(get_plato_service),
):
    dish = service.delete_dish(dish_id)
    return DeleteResponse(message="Plato marcado como no disponible", id=dish.id)
