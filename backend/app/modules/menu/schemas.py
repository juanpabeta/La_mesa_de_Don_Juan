"""DTOs del menú."""
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class PlatoCreate(BaseModel):
    """Alta de plato."""
    nombre: str
    categoria: str
    precio: Decimal = Field(gt=0)
    tiempo_estimado_min: int = Field(gt=0)


class PlatoRead(PlatoCreate):
    """Lectura de plato."""
    model_config = ConfigDict(from_attributes=True)
    id_plato: int
    activo: bool
    agotado: bool = False


class PlatoUpdate(BaseModel):
    """Campos modificables de un plato."""
    nombre: str | None = None
    categoria: str | None = None
    precio: Decimal | None = Field(default=None, gt=0)
    tiempo_estimado_min: int | None = Field(default=None, gt=0)


class PlatoAgotado(BaseModel):
    """Disponibilidad del plato."""
    agotado: bool
