"""DTOs de entrada y salida de estadísticas y exportaciones."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ReporteTiemposResponse(BaseModel):
    desde: date
    hasta: date
    pedidos_completados: int
    tiempo_promedio_minutos: Decimal | None
    tiempo_maximo_minutos: int | None


class ReportePerdidasCSV(BaseModel):
    desde: date | None = None
    hasta: date | None = None
    filename: str = Field(default="incidencias.csv")
