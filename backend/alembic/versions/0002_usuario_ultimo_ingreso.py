"""Track the most recent successful user login."""

import sqlalchemy as sa
from alembic import op

revision = "0002_usuario_ultimo_ingreso"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuario", sa.Column("ultimo_ingreso_en", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("usuario", "ultimo_ingreso_en")
