"""DTOs de autenticación y sesión; no dependen de la capa de persistencia."""

from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    correo: EmailStr = Field(validation_alias=AliasChoices("correo", "email"))
    contrasena: str = Field(
        min_length=1,
        max_length=128,
        validation_alias=AliasChoices("contrasena", "password"),
    )

    @field_validator("contrasena")
    @classmethod
    def bcrypt_password_fits(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña supera el límite de 72 bytes de bcrypt")
        return value


class TokenResponse(BaseModel):
    message: str = "Sesión iniciada"
    token_type: Literal["cookie"] = "cookie"
    expires_at: datetime


class UserSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_completo: str
    email: EmailStr
    roles: list[str]
