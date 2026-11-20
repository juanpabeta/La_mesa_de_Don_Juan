"""Rutas de administración de usuarios."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioRead, UsuarioUpdate
from app.modules.usuarios.services import create_user, update_user
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.get("",response_model = list[UsuarioRead])
async def list_users(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Lista todos los usuarios."""
    usuarios = (await db.scalars(select(Usuario))).all()
    return [
    {
        "id_usuario": usuario.id_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "estado": usuario.estado,
        "roles": [rol.nombre for rol in usuario.roles],
    }
    for usuario in usuarios
]


@router.post("", response_model=UsuarioRead)
async def create(data: UsuarioCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Crea un empleado."""
    existente = await db.scalar(select(Usuario).where(Usuario.correo == str(data.correo)))
    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo",
        )
    try:
        user = await create_user(db, data)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo",
        ) from exc
    return {"id_usuario": user.id_usuario, "nombres": user.nombres, "apellidos": user.apellidos, "correo": user.correo, "estado": user.estado, "roles": [r.nombre for r in user.roles]}



@router.put("/{user_id}", response_model=UsuarioRead)
async def update(user_id: int, data: UsuarioUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Actualiza un usuario."""
    user = await db.scalar(select(Usuario).where(Usuario.id_usuario == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user = await update_user(db, user, data)
    return {"id_usuario": user.id_usuario, "nombres": user.nombres, "apellidos": user.apellidos, "correo": user.correo, "estado": user.estado, "roles": [r.nombre for r in user.roles]}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(user_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Desactiva un usuario sin borrar su historial."""
    user = await db.scalar(select(Usuario).where(Usuario.id_usuario == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.estado = False
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
