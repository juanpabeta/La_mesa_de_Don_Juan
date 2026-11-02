"""Limitador local de intentos de autenticación.

Sirve como protección inmediata para una instancia. En un despliegue con varias
réplicas debe sustituirse por un backend compartido, por ejemplo Redis.
"""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic


WINDOW_SECONDS = 300
MAX_FAILURES = 10

_failures: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def is_blocked(key: str) -> bool:
    now = monotonic()
    with _lock:
        attempts = _failures[key]
        while attempts and now - attempts[0] >= WINDOW_SECONDS:
            attempts.popleft()
        return len(attempts) >= MAX_FAILURES


def record_failure(key: str) -> None:
    now = monotonic()
    with _lock:
        attempts = _failures[key]
        while attempts and now - attempts[0] >= WINDOW_SECONDS:
            attempts.popleft()
        attempts.append(now)


def clear_failures(key: str) -> None:
    with _lock:
        _failures.pop(key, None)
