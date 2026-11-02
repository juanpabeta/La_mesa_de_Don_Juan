"""Endpoints HTTP para administración de empleados y roles."""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import DatabaseSession, require_roles
from app.modules.usuarios.repositories import UsuarioRepository
from app.modules.usuarios.schemas import DeleteResponse, RoleUpdate, UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.modules.usuarios.services import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def get_usuario_service(db: DatabaseSession) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))


@router.get("", response_model=list[UsuarioResponse])
def list_users(
    _actor=Depends(require_roles("ADMIN")), service: UsuarioService = Depends(get_usuario_service)
):
    return service.list_users()


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UsuarioCreate,
    _actor=Depends(require_roles("ADMIN")),
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.create_user(
        nombre_completo=payload.nombre_completo,
        email=str(payload.email),
        password=payload.password,
        roles=payload.roles,
    )


@router.put("/{user_id}", response_model=UsuarioResponse)
def update_user(
    user_id: int,
    payload: UsuarioUpdate,
    _actor=Depends(require_roles("ADMIN")),
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.update_user(user_id, payload.model_dump(exclude_unset=True))


@router.put("/{user_id}/roles", response_model=UsuarioResponse)
def update_roles(
    user_id: int,
    payload: RoleUpdate,
    _actor=Depends(require_roles("ADMIN")),
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.update_roles(user_id, payload.roles)


@router.delete("/{user_id}", response_model=DeleteResponse)
def delete_user(
    user_id: int,
    _actor=Depends(require_roles("ADMIN")),
    service: UsuarioService = Depends(get_usuario_service),
):
    user = service.delete_user(user_id)
    return DeleteResponse(message="Usuario desactivado correctamente", id=user.id)
