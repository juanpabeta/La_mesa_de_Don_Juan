"""Alinea columnas operativas de menú e incidencias."""
from alembic import op
import sqlalchemy as sa

revision = "0003_operational_contract"
down_revision = "0002_seed_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("platos", sa.Column("agotado", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("incidencias_pedido", sa.Column("prioridad", sa.String(20), nullable=False, server_default="MEDIA"))
    op.add_column("incidencias_pedido", sa.Column("estado", sa.String(20), nullable=False, server_default="ABIERTA"))
    op.add_column("pedidos", sa.Column("propina", sa.Numeric(10, 2), nullable=False, server_default="0"))
    op.execute(sa.text("INSERT INTO roles (nombre, descripcion) VALUES ('Cocinero', 'Ejecuta cocina'), ('Cajero', 'Gestiona cobros') ON CONFLICT (nombre) DO NOTHING"))


def downgrade() -> None:
    op.drop_column("pedidos", "propina")
    op.drop_column("incidencias_pedido", "estado")
    op.drop_column("incidencias_pedido", "prioridad")
    op.drop_column("platos", "agotado")
