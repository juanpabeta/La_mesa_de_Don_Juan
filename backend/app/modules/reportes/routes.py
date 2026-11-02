"""Endpoints HTTP para estadísticas y descarga de informes CSV."""

from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.core.dependencies import DatabaseSession, require_roles
from app.modules.reportes.repositories import ReporteRepository
from app.modules.reportes.schemas import ReporteTiemposResponse
from app.modules.reportes.services import ReporteService
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def get_reporte_service(db: DatabaseSession) -> ReporteService:
    return ReporteService(ReporteRepository(db))


@router.get("/tiempos", response_model=ReporteTiemposResponse)
def order_times(
    desde: date,
    hasta: date,
    _actor: Usuario = Depends(require_roles("ADMIN")),
    service: ReporteService = Depends(get_reporte_service),
):
    return service.order_times(desde, hasta)


@router.get("/exportar")
def export_incidents(
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    _actor: Usuario = Depends(require_roles("ADMIN")),
    service: ReporteService = Depends(get_reporte_service),
):
    filename, content = service.export_incidents(desde, hasta)
    return StreamingResponse(
        BytesIO(content.encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
