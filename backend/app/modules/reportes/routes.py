"""Rutas de reportes."""
import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.modules.pedidos.models import Pedido
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/tiempos")
async def timing_report(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Calcula métricas básicas de entrega."""
    row = (await db.execute(select(func.count(Pedido.id_pedido), func.avg(func.extract("epoch", Pedido.fecha_hora_entrega - Pedido.fecha_hora_creacion)), func.sum(cast(Pedido.es_retrasado, Integer))).where(Pedido.fecha_hora_entrega.is_not(None)))).one()
    return {"pedidos_entregados": row[0], "promedio_segundos": float(row[1] or 0), "pedidos_retrasados": int(row[2] or 0)}


@router.get("/exportar")
async def export_csv(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Exporta el histórico de pedidos como CSV."""
    pedidos = (await db.scalars(select(Pedido).order_by(Pedido.id_pedido))).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id_pedido", "id_mesa", "estado", "fecha_creacion", "fecha_entrega", "es_retrasado"])
    for pedido in pedidos:
        writer.writerow([pedido.id_pedido, pedido.id_mesa, pedido.estado, pedido.fecha_hora_creacion, pedido.fecha_hora_entrega, pedido.es_retrasado])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=pedidos.csv"})
