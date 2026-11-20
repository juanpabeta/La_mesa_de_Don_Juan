"""Impresión térmica ESC/POS aislada de PostgreSQL."""

import asyncio
import socket


async def print_ticket(lines: list[str], host: str = "127.0.0.1", port: int = 9100) -> None:
    """Envía un ticket por puerto 9100 sin compartir la transacción de datos."""

    esc_pos = b"\x1b@" + "\n".join(lines).encode("utf-8", errors="replace") + b"\n\n\n\x1dV\x00"

    def send() -> None:
        with socket.create_connection((host, port), timeout=3) as connection:
            connection.sendall(esc_pos)

    await asyncio.to_thread(send)
