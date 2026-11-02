"""Procesamiento de promedios y generación de exportaciones CSV."""

import csv
import io
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from app.core.exceptions import BusinessRuleError
from app.modules.reportes.repositories import ReporteRepository


class ReporteService:
    def __init__(self, repository: ReporteRepository):
        self.repository = repository

    def order_times(self, desde: date, hasta: date) -> dict[str, object]:
        if desde > hasta:
            raise BusinessRuleError("La fecha inicial no puede ser posterior a la fecha final")
        count, average_seconds, max_seconds = self.repository.completed_order_durations(desde, hasta)
        average_minutes = (
            (Decimal(str(average_seconds)) / Decimal(60)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if average_seconds is not None
            else None
        )
        max_minutes = int(max_seconds // 60) if max_seconds is not None else None
        return {
            "desde": desde,
            "hasta": hasta,
            "pedidos_completados": count,
            "tiempo_promedio_minutos": average_minutes,
            "tiempo_maximo_minutos": max_minutes,
        }

    def export_incidents(self, desde: date | None, hasta: date | None) -> tuple[str, str]:
        if desde is not None and hasta is not None and desde > hasta:
            raise BusinessRuleError("La fecha inicial no puede ser posterior a la fecha final")
        if desde is not None and hasta is not None and hasta - desde > timedelta(days=366):
            raise BusinessRuleError("El rango máximo de exportación es de 366 días")
        rows = self.repository.list_incidents(desde, hasta)
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["id", "pedido_id", "registrada_por_id", "tipo", "descripcion", "creada_en", "resuelta_en"])
        for row in rows:
            writer.writerow(
                [
                    row.id,
                    row.pedido_id,
                    row.registrada_por_id,
                    row.tipo,
                    self._safe_csv_value(row.descripcion),
                    row.creada_en.isoformat(),
                    row.resuelta_en.isoformat() if row.resuelta_en else "",
                ]
            )
        return "incidencias.csv", output.getvalue()

    @staticmethod
    def _safe_csv_value(value: str) -> str:
        """Evita que hojas de cálculo interpreten texto como fórmula."""
        return f"'{value}" if value[:1] in {"=", "+", "-", "@"} else value
