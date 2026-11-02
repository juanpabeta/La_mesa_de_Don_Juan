"""Endpoints HTTP para inicio, cierre y consulta de sesión."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.config import settings
from app.core.dependencies import DatabaseSession, get_current_user
from app.core.exceptions import AuthenticationError
from app.modules.auth.repositories import AuthRepository
from app.modules.auth.schemas import LoginRequest, TokenResponse, UserSession
from app.modules.auth.services import AuthService
from app.modules.auth.rate_limit import clear_failures, is_blocked, record_failure
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def get_auth_service(db: DatabaseSession) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, response: Response, service: AuthService = Depends(get_auth_service)):
    email = str(payload.correo).strip().lower()
    client_host = request.client.host if request.client else "unknown"
    rate_key = f"{client_host}:{email}"
    if is_blocked(rate_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intenta nuevamente más tarde.",
            headers={"Retry-After": "300"},
        )
    try:
        token, expires_at = service.login(
            email=email,
            password=payload.contrasena,
            user_agent=request.headers.get("user-agent"),
        )
    except AuthenticationError:
        record_failure(rate_key)
        raise
    clear_failures(rate_key)
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_minutes * 60,
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return TokenResponse(expires_at=expires_at)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def logout(request: Request, service: AuthService = Depends(get_auth_service)) -> Response:
    token = request.cookies.get(settings.auth_cookie_name)
    if not token:
        authorization = request.headers.get("Authorization", "")
        scheme, separator, credentials = authorization.partition(" ")
        if separator and scheme.lower() == "bearer":
            token = credentials.strip()
    service.logout(token)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
    return response


@router.get("/me", response_model=UserSession)
def me(user: Usuario = Depends(get_current_user)) -> UserSession:
    return UserSession(
        id=user.id,
        nombre_completo=user.nombre_completo,
        email=user.email,
        roles=[role.nombre for role in user.roles],
    )
