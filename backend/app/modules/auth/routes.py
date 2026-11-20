"""Rutas de autenticación."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.modules.auth.schemas import CurrentUserResponse, LoginRequest, LoginResponse
from app.modules.usuarios.services import authenticate
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)) -> object:
    """Endpoint público de autenticación; devuelve JWT y establece cookie."""
    from fastapi import HTTPException
    user = await authenticate(db, str(data.correo), data.contraseña)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_access_token(user.id_usuario, [role.nombre for role in user.roles])
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=get_settings().cookie_secure,
        samesite="lax",
        path="/",
    )
    return {"id_usuario": user.id_usuario, "nombres": user.nombres, "apellidos": user.apellidos, "correo": user.correo, "estado": user.estado, "roles": [r.nombre for r in user.roles], "access_token": token}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, current_user: Usuario = Depends(get_current_user)) -> None:
    """Cierra una sesión autenticada eliminando su cookie."""
    response.delete_cookie("access_token", path="/")


@router.get("/me", response_model=CurrentUserResponse)
async def me(current_user: Usuario = Depends(get_current_user)) -> object:
    """Devuelve el usuario actual."""
    return {"id_usuario": current_user.id_usuario, "nombres": current_user.nombres, "apellidos": current_user.apellidos, "correo": current_user.correo, "estado": current_user.estado, "roles": [r.nombre for r in current_user.roles]}
