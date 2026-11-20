"""Rutas del catálogo."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.modules.menu.models import Plato
from app.modules.menu.schemas import PlatoAgotado, PlatoCreate, PlatoRead, PlatoUpdate
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("", response_model=list[PlatoRead])
async def list_menu(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Lista platos activos."""
    return list((await db.scalars(select(Plato).where(Plato.activo.is_(True)))).all())


@router.post("", response_model=PlatoRead)
async def create_plato(data: PlatoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Crea un plato."""
    plato = Plato(**data.model_dump())
    db.add(plato)
    await db.commit()
    await db.refresh(plato)
    return plato


@router.put("/{plato_id}", response_model=PlatoRead)
async def replace_plato(plato_id: int, data: PlatoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Reemplaza los datos editables de un plato."""
    plato = await db.get(Plato, plato_id)
    if plato is None:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    for field, value in data.model_dump().items():
        setattr(plato, field, value)
    await db.commit()
    await db.refresh(plato)
    return plato



@router.patch("/{plato_id}/agotado", response_model=PlatoRead)
async def set_agotado(plato_id: int, data: PlatoAgotado, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador", "Cocina"]))):
    """Marca un plato agotado o vuelve a habilitarlo."""
    plato = await db.get(Plato, plato_id)
    if plato is None:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    plato.agotado = data.agotado
    await db.commit()
    await db.refresh(plato)
    return plato
