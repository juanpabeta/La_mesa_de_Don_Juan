"""DTOs de comandas."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class DetalleCreate(BaseModel):
    """Línea solicitada."""
    id_plato: int
    cantidad: int = Field(gt=0)
    observaciones: str | None = None


class PedidoCreate(BaseModel):
    """Datos de creación de comanda."""
    id_mesa: int
    detalles: list[DetalleCreate] = Field(min_length=1)


class PedidoUpdate(BaseModel):
    """Detalles para reemplazar los de una comanda pendiente."""
    detalles: list[DetalleCreate] = Field(min_length=1)


class PropinaUpdate(BaseModel):
    """Propina voluntaria expresada en COP."""
    propina: Decimal = Field(ge=0)


class PedidoEstado(BaseModel):
    """Cambio de estado."""
    estado: Literal["PENDIENTE", "EN_PREPARACION", "LISTO", "ENTREGADO", "CANCELADO"]
    causa: str | None = None


class DetalleRead(BaseModel):
    """Línea persistida de una comanda."""
    model_config = ConfigDict(from_attributes=True)
    id_detalle: int
    id_plato: int
    nombre: str
    cantidad: int
    precio_unitario: Decimal
    observaciones: str | None = None


class PedidoRead(BaseModel):
    """Lectura completa compatible con el KDS y el módulo de pedidos."""
    model_config = ConfigDict(from_attributes=True)
    id_pedido: int
    id_mesa: int
    numero_mesa: int
    id_usuario: int
    mesero: str | None = None
    estado: str
    fecha_hora_creacion: datetime
    fecha_hora_entrega: datetime | None = None
    es_retrasado: bool
    propina: Decimal = Decimal("0")
    detalles: list[DetalleRead]
