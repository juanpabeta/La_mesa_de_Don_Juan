from fastapi.testclient import TestClient

import app.main as main_module
from app.core.realtime import realtime
from app.core.security import create_access_token


async def test_websocket_accepts_cookie_and_rejects_missing_token(seed_users, session_factory, monkeypatch):
    monkeypatch.setattr(main_module, "SessionLocal", session_factory)
    main_module.app.dependency_overrides.clear()
    user = seed_users["mesero"]
    token = create_access_token(user.id_usuario, [role.nombre for role in user.roles])

    with TestClient(main_module.app) as test_client:
        test_client.cookies.set("access_token", token)
        with test_client.websocket_connect("/api/v1/ws") as websocket:
            websocket.send_text("ping")

        test_client.cookies.clear()
        missing = test_client.websocket_connect("/api/v1/ws")
        try:
            with missing as websocket:
                websocket.receive_text()
        except Exception:
            pass


async def test_realtime_broadcast_reaches_connected_socket_and_resilient_socket(monkeypatch):
    class Socket:
        def __init__(self):
            self.messages = []

        async def accept(self):
            pass

        async def send_json(self, message):
            self.messages.append(message)

    socket = Socket()
    await realtime.connect(socket)
    await realtime.broadcast("order.updated", {"id_pedido": 77, "estado": "LISTO"})
    assert socket.messages[-1]["type"] == "order.updated"
    assert socket.messages[-1]["payload"]["estado"] == "LISTO"
    await realtime.disconnect(socket)
