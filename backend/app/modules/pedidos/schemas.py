"""DTOs validados para comandas, tickets y transiciones de estado."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EstadoPedido = Literal["PENDIENTE", "EN_PREPARACION", "LISTO", "ENTREGADO", "CANCELADO"]


class DetallePedidoCreate(BaseModel):
    plato_id: int = Field(gt=0)
    cantidad: int = Field(gt=0, le=100)
    notas: str | None = Field(default=None, max_length=500)


class PedidoCreate(BaseModel):
    mesa_id: int = Field(gt=0)
    detalles: list[DetallePedidoCreate] = Field(min_length=1, max_length=50)
    notas: str | None = Field(default=None, max_length=2000)


class DetallePedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plato_id: int
    nombre_plato: str
    cantidad: int
    precio_unitario: Decimal
    tiempo_preparacion_minutos: int
    notas: str | None


class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mesa_id: int
    creado_por_id: int
    estado: EstadoPedido
    creado_en: datetime
    inicio_preparacion_en: datetime | None
    listo_en: datetime | None
    entregado_en: datetime | None
    cancelado_en: datetime | None
    retrasado: bool
    retraso_marcado_en: datetime | None
    notas: str | None
    detalles: list[DetallePedidoResponse]


class TicketPedidoResponse(PedidoResponse):
    numero_mesa: int
    minutos_estimados: int
    minutos_transcurridos: int


class CambiarEstadoDTO(BaseModel):
    estado: EstadoPedido


class DeleteResponse(BaseModel):
    message: str
    id: int
