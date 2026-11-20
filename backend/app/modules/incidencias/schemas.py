"""DTOs de incidencias."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class IncidenciaCreate(BaseModel):
    """Datos de reporte."""
    id_pedido: int
    tipo_error: str = Field(min_length=1)
    descripcion: str = Field(min_length=1)
    prioridad: str = "MEDIA"


class IncidenciaRead(IncidenciaCreate):
    """Lectura de incidencia."""
    model_config = ConfigDict(from_attributes=True)
    id_incidencia: int
    id_usuario: int
    fecha_registro: datetime
    estado: str = "ABIERTA"


class IncidenciaUpdate(BaseModel):
    """Campos modificables de una incidencia."""
    tipo_error: str | None = Field(default=None, min_length=1)
    descripcion: str | None = Field(default=None, min_length=1)
    prioridad: str | None = None
    estado: str | None = None
