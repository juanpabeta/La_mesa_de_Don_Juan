"""Crea los roles base del sistema."""
from alembic import op
import sqlalchemy as sa


revision = "0002_seed_roles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Inserta los roles requeridos por la aplicación."""
    op.execute(
        sa.text(
            """
            INSERT INTO roles (nombre, descripcion)
            VALUES
                ('Administrador', 'Administrador del sistema'),
                ('Mesero', 'Gestiona mesas y pedidos'),
                ('Cocina', 'Gestiona la preparación de pedidos')
            ON CONFLICT (nombre) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    """Elimina únicamente los roles base."""
    roles = sa.table("roles", sa.column("nombre", sa.String))
    op.execute(
        roles.delete().where(
            roles.c.nombre.in_(["Administrador", "Mesero", "Cocina"])
        )
    )
