"""DTOs de mesas."""
from pydantic import BaseModel, ConfigDict, Field


class MesaCreate(BaseModel):
    """Alta de mesa."""
    numero_mesa: int = Field(gt=0)
    zona: str
    capacidad: int = Field(gt=0)


class MesaRead(MesaCreate):
    """Lectura de mesa."""
    model_config = ConfigDict(from_attributes=True)
    id_mesa: int
    estado: str
    activa: bool


class MesaUpdate(BaseModel):
    """Campos modificables de una mesa."""
    numero_mesa: int | None = Field(default=None, gt=0)
    zona: str | None = None
    capacidad: int | None = Field(default=None, gt=0)
    estado: str | None = None
    activa: bool | None = None
