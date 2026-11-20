"""Migración inicial generada desde los modelos."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea el esquema inicial."""
    op.create_table("roles", sa.Column("id_rol", sa.Integer(), primary_key=True), sa.Column("nombre", sa.String(80), nullable=False, unique=True), sa.Column("descripcion", sa.String(255), nullable=False, server_default=""))
    op.create_table("usuarios", sa.Column("id_usuario", sa.Integer(), primary_key=True), sa.Column("nombres", sa.String(100), nullable=False), sa.Column("apellidos", sa.String(100), nullable=False), sa.Column("correo", sa.String(255), nullable=False, unique=True), sa.Column("hash_contrasena", sa.String(255), nullable=False), sa.Column("estado", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_usuarios_correo", "usuarios", ["correo"], unique=False)
    op.create_table("mesas", sa.Column("id_mesa", sa.Integer(), primary_key=True), sa.Column("numero_mesa", sa.Integer(), nullable=False, unique=True), sa.Column("zona", sa.String(80), nullable=False), sa.Column("capacidad", sa.Integer(), nullable=False), sa.Column("estado", sa.String(20), nullable=False, server_default="Disponible"), sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.true()), sa.CheckConstraint("numero_mesa > 0"), sa.CheckConstraint("capacidad > 0"))
    op.create_table("platos", sa.Column("id_plato", sa.Integer(), primary_key=True), sa.Column("nombre", sa.String(150), nullable=False), sa.Column("categoria", sa.String(80), nullable=False), sa.Column("precio", sa.Numeric(10, 2), nullable=False), sa.Column("tiempo_estimado_min", sa.Integer(), nullable=False), sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()), sa.CheckConstraint("precio > 0"), sa.CheckConstraint("tiempo_estimado_min > 0"))
    op.create_table("usuario_rol", sa.Column("id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True), sa.Column("id_rol", sa.Integer(), sa.ForeignKey("roles.id_rol", ondelete="CASCADE"), primary_key=True))
    op.create_table("pedidos", sa.Column("id_pedido", sa.Integer(), primary_key=True), sa.Column("id_mesa", sa.Integer(), sa.ForeignKey("mesas.id_mesa"), nullable=False), sa.Column("id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id_usuario"), nullable=False), sa.Column("estado", sa.String(30), nullable=False, server_default="PENDIENTE"), sa.Column("fecha_hora_creacion", sa.DateTime(timezone=True), nullable=False), sa.Column("fecha_hora_entrega", sa.DateTime(timezone=True)), sa.Column("es_retrasado", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table("detalles_pedido", sa.Column("id_detalle", sa.Integer(), primary_key=True), sa.Column("id_pedido", sa.Integer(), sa.ForeignKey("pedidos.id_pedido", ondelete="CASCADE"), nullable=False), sa.Column("id_plato", sa.Integer(), sa.ForeignKey("platos.id_plato", ondelete="RESTRICT"), nullable=False), sa.Column("cantidad", sa.Integer(), nullable=False), sa.Column("precio_unitario", sa.Numeric(10, 2), nullable=False), sa.Column("observaciones", sa.Text()))
    op.create_table("incidencias_pedido", sa.Column("id_incidencia", sa.Integer(), primary_key=True), sa.Column("id_pedido", sa.Integer(), sa.ForeignKey("pedidos.id_pedido"), nullable=False), sa.Column("id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id_usuario"), nullable=False), sa.Column("tipo_error", sa.String(80), nullable=False), sa.Column("descripcion", sa.Text(), nullable=False), sa.Column("fecha_registro", sa.DateTime(timezone=True), nullable=False))


def downgrade() -> None:
    """Revierte el esquema inicial."""
    op.drop_index("ix_usuarios_correo", table_name="usuarios")
    for table in ("incidencias_pedido", "detalles_pedido", "pedidos", "usuario_rol", "platos", "mesas", "usuarios", "roles"):
        op.drop_table(table)
