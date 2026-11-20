"""DTOs de autenticación."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Credenciales para iniciar sesión."""

    correo: EmailStr
    contraseña: str = Field(min_length=8, max_length=128)

    @field_validator("contraseña")
    @classmethod
    def bcrypt_password_fits(cls, value: str) -> str:
        """Rechaza contraseñas que exceden el límite de bcrypt."""
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña supera el límite de 72 bytes de bcrypt")
        return value

    @field_validator("contraseña")
    @classmethod
    def password_not_empty(cls, value: str) -> str:
        """Rechaza contraseñas vacías."""
        if not value.strip():
            raise ValueError("La contraseña no puede estar vacía")
        return value
    
class CurrentUserResponse(BaseModel):
    """Datos públicos del usuario autenticado."""

    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nombres: str
    apellidos: str
    correo: EmailStr
    estado: bool
    roles: list[str]


class LoginResponse(CurrentUserResponse):
    """Respuesta de inicio de sesión; access_token se puede autorizar en Swagger."""
    access_token: str

