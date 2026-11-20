"""Rutas de incidencias."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.modules.incidencias.models import IncidenciaPedido
from app.modules.incidencias.schemas import IncidenciaCreate, IncidenciaRead, IncidenciaUpdate
from app.modules.pedidos.models import Pedido
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/incidencias", tags=["incidencias"])


@router.post("", response_model=IncidenciaRead)
async def create_incident(data: IncidenciaCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Registra una incidencia con su auditor."""
    if await db.get(Pedido, data.id_pedido) is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    item = IncidenciaPedido(**data.model_dump(), id_usuario=current_user.id_usuario)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("", response_model=list[IncidenciaRead])
async def list_incidents(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Lista incidencias para administración."""
    return list((await db.scalars(select(IncidenciaPedido).where(IncidenciaPedido.estado != "ELIMINADA").order_by(IncidenciaPedido.fecha_registro.desc()))).all())


@router.patch("/{incidencia_id}", response_model=IncidenciaRead)
async def update_incident(incidencia_id: int, data: IncidenciaUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Actualiza una incidencia."""
    item = await db.get(IncidenciaPedido, incidencia_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{incidencia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(incidencia_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Elimina una incidencia."""
    item = await db.get(IncidenciaPedido, incidencia_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    item.estado = "ELIMINADA"
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
