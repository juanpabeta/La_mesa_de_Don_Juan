"""Crea la primera cuenta ADMIN de forma interactiva.

Ejecutar desde backend/ después de aplicar las migraciones:
python -m app.core.bootstrap
"""

from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.usuarios.repositories import UsuarioRepository


def main() -> None:
    email = TypeAdapter(EmailStr).validate_python(input("Correo del administrador: ")).strip().lower()
    password = getpass("Contraseña (mínimo 10 caracteres): ")
    confirmation = getpass("Confirma la contraseña: ")
    if len(password) < 10:
        raise SystemExit("La contraseña debe tener al menos 10 caracteres")
    if len(password.encode("utf-8")) > 72:
        raise SystemExit("La contraseña supera el límite de 72 bytes de bcrypt")
    if password != confirmation:
        raise SystemExit("Las contraseñas no coinciden")

    with SessionLocal() as db:
        repository = UsuarioRepository(db)
        if repository.email_exists(email):
            raise SystemExit("Ya existe una cuenta con ese correo")
        roles = repository.get_roles_by_names(["ADMIN"])
        if not roles:
            raise SystemExit("No existe el rol ADMIN; primero aplica las migraciones")
        repository.create(
            nombre_completo=input("Nombre completo: ").strip(),
            email=email,
            password_hash=hash_password(password),
            roles=roles,
        )
    print("Cuenta ADMIN creada.")


if __name__ == "__main__":
    try:
        main()
    except ValidationError as exc:
        raise SystemExit("El correo no tiene un formato válido") from exc
