"""DTOs de entrada y salida para auditoría de incidencias."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TipoIncidencia = Literal["PERDIDA", "ENTREGA_ERRONEA", "DEMORA", "CANCELACION", "MESA_EQUIVOCADA", "OTRA"]


class IncidenciaCreate(BaseModel):
    pedido_id: int | None = Field(default=None, gt=0)
    tipo: TipoIncidencia
    descripcion: str = Field(min_length=5, max_length=4000)


class IncidenciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pedido_id: int | None
    registrada_por_id: int
    tipo: str
    descripcion: str
    creada_en: datetime
    resuelta_en: datetime | None


class DeleteResponse(BaseModel):
    message: str
    id: int
