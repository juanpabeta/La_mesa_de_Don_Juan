"""Punto de entrada de La mesa de Don Juan."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError
from app.core.realtime import realtime
from app.modules.usuarios.models import Usuario
from sqlalchemy import select
from app.modules.auth.routes import router as auth_router
from app.modules.usuarios.routes import router as usuarios_router
from app.modules.mesas.routes import router as mesas_router
from app.modules.menu.routes import router as menu_router
from app.modules.pedidos.routes import router as pedidos_router
from app.modules.incidencias.routes import router as incidencias_router
from app.modules.reportes.routes import router as reportes_router

app = FastAPI(title="La mesa de Don Juan API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth_router, usuarios_router, mesas_router, menu_router, pedidos_router, incidencias_router, reportes_router):
    app.include_router(router, prefix="/api/v1")


@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Mantiene una suscripción realtime validando el usuario y su estado."""
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (AuthenticationError, KeyError, TypeError, ValueError):
        await websocket.close(code=1008)
        return
    async with SessionLocal() as db:
        user = await db.scalar(select(Usuario).where(Usuario.id_usuario == user_id, Usuario.estado.is_(True)))
    if user is None:
        await websocket.close(code=1008)
        return
    await realtime.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await realtime.disconnect(websocket)


@app.get("/health")
async def health() -> dict[str, str]:
    """Comprobación de disponibilidad."""
    return {"status": "ok"}
