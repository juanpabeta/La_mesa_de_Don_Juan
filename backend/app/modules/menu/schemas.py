"""DTOs validados del catálogo de platos."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PlatoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: str | None = Field(default=None, max_length=2000)
    categoria: str | None = Field(default=None, max_length=80)
    precio: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    tiempo_preparacion_minutos: int = Field(default=15, gt=0, le=1440)


class PlatoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    descripcion: str | None = Field(default=None, max_length=2000)
    categoria: str | None = Field(default=None, max_length=80)
    precio: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    tiempo_preparacion_minutos: int | None = Field(default=None, gt=0, le=1440)
    disponible: bool | None = None


class PlatoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    categoria: str | None
    precio: Decimal
    tiempo_preparacion_minutos: int
    disponible: bool
    creado_en: datetime
    actualizado_en: datetime


class DeleteResponse(BaseModel):
    message: str
    id: int
