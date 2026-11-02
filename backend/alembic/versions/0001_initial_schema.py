"""Create the initial restaurant order management schema."""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    roles = op.create_table(
        "rol",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(length=50), nullable=False, unique=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
    )
    op.bulk_insert(
        roles,
        [
            {"nombre": "ADMIN", "descripcion": "Administración del sistema"},
            {"nombre": "GERENTE", "descripcion": "Gestión operativa del restaurante"},
            {"nombre": "MESERO", "descripcion": "Registro y seguimiento de comandas"},
            {"nombre": "COCINA", "descripcion": "Preparación y actualización de comandas"},
        ],
    )
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre_completo", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_usuario_email", "usuario", ["email"], unique=True)
    op.create_table(
        "usuario_rol",
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("rol_id", sa.Integer(), sa.ForeignKey("rol.id", ondelete="CASCADE"), primary_key=True),
        sa.UniqueConstraint("usuario_id", "rol_id", name="uq_usuario_rol"),
    )
    op.create_table(
        "sesion_token",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
    )
    op.create_index("ix_sesion_token_user_id", "sesion_token", ["user_id"])
    op.create_index("ix_sesion_token_jti", "sesion_token", ["jti"], unique=True)
    op.create_index("ix_sesion_token_expires_at", "sesion_token", ["expires_at"])
    op.create_table(
        "mesa",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numero", sa.Integer(), nullable=False, unique=True),
        sa.Column("zona", sa.String(length=80), nullable=True),
        sa.Column("capacidad", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=20), server_default="LIBRE", nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("capacidad > 0", name="ck_mesa_capacidad_positiva"),
        sa.CheckConstraint("estado IN ('LIBRE', 'OCUPADA', 'INACTIVA')", name="ck_mesa_estado"),
    )
    op.create_table(
        "plato",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("categoria", sa.String(length=80), nullable=True),
        sa.Column("precio", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("tiempo_preparacion_minutos", sa.Integer(), server_default="15", nullable=False),
        sa.Column("disponible", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("precio >= 0", name="ck_plato_precio_no_negativo"),
        sa.CheckConstraint("tiempo_preparacion_minutos > 0", name="ck_plato_tiempo_positivo"),
    )
    op.create_index("ix_plato_nombre", "plato", ["nombre"], unique=True)
    op.create_index("ix_plato_categoria", "plato", ["categoria"])
    op.create_index("ix_plato_disponible", "plato", ["disponible"])
    op.create_table(
        "pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mesa_id", sa.Integer(), sa.ForeignKey("mesa.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("creado_por_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("estado", sa.String(length=24), nullable=False, server_default="PENDIENTE"),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("inicio_preparacion_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("listo_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("entregado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrasado", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("retraso_marcado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "estado IN ('PENDIENTE', 'EN_PREPARACION', 'LISTO', 'ENTREGADO', 'CANCELADO')",
            name="ck_pedido_estado",
        ),
    )
    op.create_index("ix_pedido_mesa_id", "pedido", ["mesa_id"])
    op.create_index("ix_pedido_estado", "pedido", ["estado"])
    op.create_table(
        "detalle_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plato_id", sa.Integer(), sa.ForeignKey("plato.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("nombre_plato", sa.String(length=120), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("tiempo_preparacion_minutos", sa.Integer(), nullable=False),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.CheckConstraint("cantidad > 0", name="ck_detalle_cantidad_positiva"),
        sa.CheckConstraint("precio_unitario >= 0", name="ck_detalle_precio_no_negativo"),
        sa.CheckConstraint("tiempo_preparacion_minutos > 0", name="ck_detalle_tiempo_positivo"),
    )
    op.create_index("ix_detalle_pedido_pedido_id", "detalle_pedido", ["pedido_id"])
    op.create_table(
        "incidencia_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido.id", ondelete="SET NULL"), nullable=True),
        sa.Column("registrada_por_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("creada_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resuelta_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_incidencia_pedido_pedido_id", "incidencia_pedido", ["pedido_id"])
    op.create_index("ix_incidencia_pedido_tipo", "incidencia_pedido", ["tipo"])


def downgrade() -> None:
    op.drop_table("incidencia_pedido")
    op.drop_table("detalle_pedido")
    op.drop_table("pedido")
    op.drop_table("plato")
    op.drop_table("mesa")
    op.drop_table("sesion_token")
    op.drop_table("usuario_rol")
    op.drop_table("usuario")
    op.drop_table("rol")
