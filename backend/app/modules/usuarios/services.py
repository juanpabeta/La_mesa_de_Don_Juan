"""Reglas de negocio para altas, bajas y roles del personal."""

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.repositories import UsuarioRepository


class UsuarioService:
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def list_users(self) -> list[Usuario]:
        return self.repository.list()

    def get_user(self, user_id: int) -> Usuario:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("No se encontró el usuario")
        return user

    def create_user(self, *, nombre_completo: str, email: str, password: str, roles: list[str]) -> Usuario:
        email = email.strip().lower()
        if self.repository.email_exists(email):
            raise ConflictError("Ya existe un usuario con ese correo")
        role_names = list(dict.fromkeys(name.strip().upper() for name in roles))
        if not role_names:
            raise BusinessRuleError("El usuario debe tener al menos un rol")
        found_roles = self.repository.get_roles_by_names(role_names)
        if {role.nombre.upper() for role in found_roles} != set(role_names):
            raise BusinessRuleError("Uno o más roles no están registrados")
        return self.repository.create(
            nombre_completo=nombre_completo.strip(),
            email=email,
            password_hash=hash_password(password),
            roles=found_roles,
        )

    def update_user(self, user_id: int, changes: dict[str, object]) -> Usuario:
        user = self.get_user(user_id)
        if not changes:
            raise BusinessRuleError("Debes indicar al menos un campo para actualizar")
        if "email" in changes:
            if changes["email"] is None:
                raise BusinessRuleError("El correo no puede estar vacío")
            email = str(changes["email"]).strip().lower()
            if self.repository.email_exists(email, exclude_id=user.id):
                raise ConflictError("Ya existe un usuario con ese correo")
            changes["email"] = email
        if "nombre_completo" in changes and changes["nombre_completo"] is not None:
            changes["nombre_completo"] = str(changes["nombre_completo"]).strip()
        if "nombre_completo" in changes and changes["nombre_completo"] is None:
            raise BusinessRuleError("El nombre no puede estar vacío")
        if "activo" in changes and changes["activo"] is None:
            raise BusinessRuleError("El estado activo debe ser verdadero o falso")
        return self.repository.update(user, changes)

    def update_roles(self, user_id: int, names: list[str]) -> Usuario:
        user = self.get_user(user_id)
        role_names = list(dict.fromkeys(name.strip().upper() for name in names))
        if not role_names:
            raise BusinessRuleError("El usuario debe tener al menos un rol")
        found_roles = self.repository.get_roles_by_names(role_names)
        if {role.nombre.upper() for role in found_roles} != set(role_names):
            raise BusinessRuleError("Uno o más roles no están registrados")
        return self.repository.update_roles(user, found_roles)

    def delete_user(self, user_id: int) -> Usuario:
        user = self.get_user(user_id)
        if not user.activo:
            raise BusinessRuleError("El usuario ya está desactivado")
        return self.repository.deactivate(user)
