"""Keep order and incident history when records are removed from normal views."""

import sqlalchemy as sa
from alembic import op

revision = "0003_auditable_deletions"
down_revision = "0002_usuario_ultimo_ingreso"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pedido", sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column("pedido", sa.Column("eliminado_por_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_pedido_eliminado_por_usuario",
        "pedido",
        "usuario",
        ["eliminado_por_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.add_column("incidencia_pedido", sa.Column("eliminada_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column("incidencia_pedido", sa.Column("eliminada_por_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_incidencia_eliminada_por_usuario",
        "incidencia_pedido",
        "usuario",
        ["eliminada_por_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_incidencia_eliminada_por_usuario", "incidencia_pedido", type_="foreignkey")
    op.drop_column("incidencia_pedido", "eliminada_por_id")
    op.drop_column("incidencia_pedido", "eliminada_en")
    op.drop_constraint("fk_pedido_eliminado_por_usuario", "pedido", type_="foreignkey")
    op.drop_column("pedido", "eliminado_por_id")
    op.drop_column("pedido", "eliminado_en")
