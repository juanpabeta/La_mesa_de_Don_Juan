"""DTOs de usuarios."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    """Datos de alta."""
    nombres: str
    apellidos: str
    correo: EmailStr
    contraseña: str = Field(min_length=8)
    roles: list[str] = ["Mesero"]


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_usuario: int
    nombres: str
    apellidos: str
    correo: EmailStr
    estado: bool
    roles: list[str]

    
class UsuarioUpdate(BaseModel):
    """Datos de actualización."""
    nombres: str | None = None
    apellidos: str | None = None
    correo: EmailStr | None = None
    contraseña: str | None = Field(default=None, min_length=8)
    estado: bool | None = None
    roles: list[str] | None = None

class LoginRequest(BaseModel):
    """Credenciales de acceso."""
    correo: EmailStr
    contraseña: str
