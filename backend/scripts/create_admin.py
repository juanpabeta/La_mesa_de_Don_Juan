"""Crea un usuario administrador para La mesa de Don Juan."""
import argparse
import asyncio
import getpass
import sys
from pathlib import Path

# Permite ejecutar el script directamente desde la carpeta backend.
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.usuarios.models import Rol, Usuario


async def create_admin(
    email: str,
    password: str,
    nombres: str,
    apellidos: str,
) -> None:
    """Crea un administrador y el rol requerido si no existen."""
    async with SessionLocal() as db:
        role = await db.scalar(select(Rol).where(Rol.nombre == "Administrador"))
        if role is None:
            role = Rol(
                nombre="Administrador",
                descripcion="Administrador del sistema",
            )
            db.add(role)
            await db.flush()

        user = await db.scalar(select(Usuario).where(Usuario.correo == email))
        if user is not None:
            if role not in user.roles:
                user.roles.append(role)
            user.estado = True
            await db.commit()
            print(f"El usuario {email} ya existía; se le asignó Administrador.")
            return

        user = Usuario(
            nombres=nombres,
            apellidos=apellidos,
            correo=email,
            hash_contraseña=hash_password(password),
            estado=True,
            roles=[role],
        )
        db.add(user)
        await db.commit()
        print(f"Administrador creado: {email}")


def main() -> None:
    """Lee los datos y ejecuta la creación del administrador."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email", help="Correo del administrador")
    parser.add_argument("--nombres", default="Admin", help="Nombres")
    parser.add_argument("--apellidos", default="Sistema", help="Apellidos")
    args = parser.parse_args()

    password = getpass.getpass("Contraseña: ")
    confirmation = getpass.getpass("Confirma la contraseña: ")
    if password != confirmation:
        parser.error("Las contraseñas no coinciden.")
    if len(password) < 8:
        parser.error("La contraseña debe tener al menos 8 caracteres.")

    asyncio.run(create_admin(args.email, password, args.nombres, args.apellidos))


if __name__ == "__main__":
    main()
