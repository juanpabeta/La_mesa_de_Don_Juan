"""Excepciones de dominio y manejadores HTTP."""
from fastapi import HTTPException, status


class DomainError(HTTPException):
    """Error controlado de reglas de negocio."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        super().__init__(status_code=status_code, detail=detail)


class BadRequestError(DomainError):
    """La solicitud contiene datos inválidos (400)."""

    def __init__(self, detail: str = "Solicitud inválida") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class AuthenticationError(DomainError):
    """Falta autenticación o las credenciales no son válidas (401)."""

    def __init__(self, detail: str = "Autenticación requerida") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedError(DomainError):
    """El usuario autenticado no tiene permisos suficientes (403)."""

    def __init__(self, detail: str = "Permisos insuficientes") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(DomainError):
    """El recurso solicitado no existe (404)."""

    def __init__(self, detail: str = "Recurso no encontrado") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(DomainError):
    """La operación entra en conflicto con el estado actual (409)."""

    def __init__(self, detail: str = "Conflicto con el estado actual del recurso") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class UnprocessableEntityError(DomainError):
    """La solicitud está bien formada, pero no se puede procesar (422)."""

    def __init__(self, detail: str = "La solicitud no se pudo procesar") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
