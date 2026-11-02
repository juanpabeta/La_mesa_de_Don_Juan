"""Excepciones de aplicación y conversión central a respuestas HTTP."""

import logging
from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    status_code = 400
    code = "application_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AuthenticationError(AppError):
    status_code = 401
    code = "authentication_error"


class AuthorizationError(AppError):
    status_code = 403
    code = "authorization_error"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class BusinessRuleError(AppError):
    status_code = 422
    code = "business_rule_violation"


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Error no controlado atendiendo %s", request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Error interno del servidor"}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unexpected_error_handler)  # type: ignore[arg-type]
