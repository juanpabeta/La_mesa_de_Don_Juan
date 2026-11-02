"""DTOs validados de mesas y disponibilidad."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MesaCreate(BaseModel):
    numero: int = Field(gt=0)
    zona: str | None = Field(default=None, max_length=80)
    capacidad: int = Field(gt=0, le=100)


class MesaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int
    zona: str | None
    capacidad: int
    estado: Literal["LIBRE", "OCUPADA", "INACTIVA"]
    creado_en: datetime


class MesaStatusUpdate(BaseModel):
    estado: Literal["LIBRE", "INACTIVA"]


class DeleteResponse(BaseModel):
    message: str
    id: int
