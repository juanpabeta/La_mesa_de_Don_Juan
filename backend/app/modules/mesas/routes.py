"""Rutas de mesas."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.modules.mesas.models import Mesa
from app.modules.mesas.schemas import MesaCreate, MesaRead, MesaUpdate
from app.modules.usuarios.models import Usuario
from app.modules.pedidos.models import Pedido


class MesaTransferir(BaseModel):
    id_mesa_destino: int = Field(gt=0)

router = APIRouter(prefix="/mesas", tags=["mesas"])


@router.get("", response_model=list[MesaRead])
async def list_mesas(zona: str | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Lista mesas activas, opcionalmente filtradas por zona."""
    query = select(Mesa).where(Mesa.activa.is_(True))
    if zona:
        query = query.where(Mesa.zona == zona)
    return list((await db.scalars(query)).all())


@router.post("", response_model=MesaRead)
async def create_mesa(data: MesaCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Crea una mesa."""
    existente = await db.scalar(
        select(Mesa.id_mesa).where(Mesa.numero_mesa == data.numero_mesa)
    )
    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una mesa con el número {data.numero_mesa}",
        )

    mesa = Mesa(**data.model_dump())
    db.add(mesa)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear la mesa por un conflicto de integridad; verifica que el número no esté ocupado",
        ) from exc
    await db.refresh(mesa)
    return mesa


@router.patch("/{mesa_id}", response_model=MesaRead)
async def update_mesa(mesa_id: int, data: MesaUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Actualiza una mesa."""
    mesa = await db.get(Mesa, mesa_id)
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    cambios = data.model_dump(exclude_unset=True)
    nuevo_numero = cambios.get("numero_mesa")
    if nuevo_numero is not None:
        existente = await db.scalar(
            select(Mesa.id_mesa).where(
                Mesa.numero_mesa == nuevo_numero,
                Mesa.id_mesa != mesa_id,
            )
        )
        if existente is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otra mesa con el número {nuevo_numero}",
            )

    for field, value in cambios.items():
        setattr(mesa, field, value)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar la mesa por un conflicto de integridad; verifica que el número no esté ocupado",
        ) from exc
    await db.refresh(mesa)
    return mesa


@router.post("/{mesa_id}/transferir", response_model=MesaRead)
async def transferir_mesa(mesa_id: int, data: MesaTransferir, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador", "Mesero", "Cajero"]))):
    """Transfiere atómicamente la comanda activa y libera la mesa origen."""
    origen = await db.scalar(select(Mesa).where(Mesa.id_mesa == mesa_id, Mesa.activa.is_(True)).with_for_update())
    destino = await db.scalar(select(Mesa).where(Mesa.id_mesa == data.id_mesa_destino, Mesa.activa.is_(True)).with_for_update())
    if origen is None or destino is None:
        raise HTTPException(status_code=404, detail="Mesa origen o destino no encontrada")
    if destino.estado != "Disponible":
        raise HTTPException(status_code=409, detail="La mesa destino no está disponible")
    pedido = await db.scalar(select(Pedido).where(Pedido.id_mesa == mesa_id, Pedido.estado.not_in(["ENTREGADO", "CANCELADO"])).with_for_update())
    if pedido is None:
        raise HTTPException(status_code=409, detail="La mesa origen no tiene una comanda activa")
    pedido.id_mesa = destino.id_mesa
    origen.estado = "Disponible"
    destino.estado = "Ocupada"
    await db.commit()
    await db.refresh(destino)
    return destino


@router.delete("/{mesa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mesa(mesa_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Desactiva una mesa y conserva los pedidos históricos."""
    mesa = await db.get(Mesa, mesa_id)
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    mesa.activa = False
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
