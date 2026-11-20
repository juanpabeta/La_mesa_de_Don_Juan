"""Gestor resiliente de conexiones WebSocket."""
from __future__ import annotations

from asyncio import Lock
from typing import Any

from fastapi import WebSocket


class RealtimeManager:
    """Administra suscripciones activas y broadcast tolerante a fallos."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, event_type: str, payload: dict[str, Any]) -> None:
        async with self._lock:
            connections = tuple(self._connections)

        message = {"type": event_type, "payload": payload}
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                await self.disconnect(websocket)


realtime = RealtimeManager()
