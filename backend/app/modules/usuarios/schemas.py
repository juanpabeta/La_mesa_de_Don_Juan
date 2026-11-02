"""DTOs de entrada y salida para empleados y roles."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None = None


class UsuarioCreate(BaseModel):
    nombre_completo: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    roles: list[str] = Field(default_factory=lambda: ["MESERO"], max_length=10)

    @field_validator("password")
    @classmethod
    def bcrypt_password_fits(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña supera el límite de 72 bytes de bcrypt")
        return value


class UsuarioUpdate(BaseModel):
    nombre_completo: str | None = Field(default=None, min_length=2, max_length=160)
    email: EmailStr | None = None
    activo: bool | None = None


class RoleUpdate(BaseModel):
    roles: list[str] = Field(min_length=1, max_length=10)


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_completo: str
    email: EmailStr
    activo: bool
    creado_en: datetime
    roles: list[RolResponse] = Field(default_factory=list)


class DeleteResponse(BaseModel):
    message: str
    id: int
