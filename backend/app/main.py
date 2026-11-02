"""Punto de entrada de FastAPI, CORS y registro de routers."""

import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.exceptions import register_exception_handlers
from app.modules.auth.routes import router as auth_router
from app.modules.incidencias.routes import router as incidencias_router
from app.modules.mesas.routes import router as mesas_router
from app.modules.menu.routes import router as menu_router
from app.modules.pedidos.routes import router as pedidos_router
from app.modules.pedidos.repositories import PedidoRepository
from app.modules.pedidos.services import PedidoService
from app.modules.mesas.repositories import MesaRepository
from app.modules.menu.repositories import PlatoRepository
from app.modules.reportes.routes import router as reportes_router
from app.modules.usuarios.routes import router as usuarios_router

logger = logging.getLogger(__name__)
DELAY_SCAN_INTERVAL_SECONDS = 60


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        if is_production:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


def _mark_overdue_orders() -> int:
    with SessionLocal() as db:
        service = PedidoService(PedidoRepository(db), MesaRepository(db), PlatoRepository(db))
        return service.mark_overdue_orders()


async def _delay_monitor() -> None:
    while True:
        try:
            marked_count = await asyncio.to_thread(_mark_overdue_orders)
            if marked_count:
                logger.info("Se marcaron %s pedidos retrasados", marked_count)
        except Exception:
            logger.exception("No se pudieron actualizar las marcas de retraso de pedidos")
        await asyncio.sleep(DELAY_SCAN_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    monitor = None
    if settings.enable_delay_monitor and settings.app_env.strip().lower() != "test":
        monitor = asyncio.create_task(_delay_monitor())
    try:
        yield
    finally:
        if monitor is not None:
            monitor.cancel()
            with suppress(asyncio.CancelledError):
                await monitor


is_production = settings.app_env.strip().lower() in {"prod", "production"}
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)
register_exception_handlers(app)

for router in (
    auth_router,
    usuarios_router,
    mesas_router,
    menu_router,
    pedidos_router,
    incidencias_router,
    reportes_router,
):
    app.include_router(router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["Sistema"])
def readiness(db=Depends(get_db)) -> dict[str, str]:
    """Indica si la aplicación puede atender tráfico dependiente de PostgreSQL."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from exc
    return {"status": "ready"}
