"""Migración inicial: crear todas las tablas de RepuBot

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabla negocios
    op.create_table(
        "negocios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("rubro", sa.String(100), nullable=False),
        sa.Column("tono", sa.String(50), nullable=True, server_default="profesional"),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("publico_objetivo", sa.Text(), nullable=True),
        sa.Column("horario", sa.String(200), nullable=True),
        sa.Column("whatsapp", sa.String(20), nullable=True),
        sa.Column("fb_page_id", sa.String(100), nullable=True),
        sa.Column("fb_access_token", sa.Text(), nullable=True),
        sa.Column("ig_account_id", sa.String(100), nullable=True),
        sa.Column("gmb_location_id", sa.String(200), nullable=True),
        sa.Column("gmb_access_token", sa.Text(), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("plan", sa.String(20), nullable=True, server_default="basico"),
        sa.Column("suscripcion_vence", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_negocios_id", "negocios", ["id"])
    op.create_index("ix_negocios_email", "negocios", ["email"], unique=True)

    # Tabla mensajes
    op.create_table(
        "mensajes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("negocio_id", sa.Integer(), nullable=False),
        sa.Column("plataforma", sa.String(30), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=True),
        sa.Column("autor", sa.String(200), nullable=True),
        sa.Column("contenido_original", sa.Text(), nullable=False),
        sa.Column("respuesta_sugerida", sa.Text(), nullable=True),
        sa.Column("respuesta_enviada", sa.Text(), nullable=True),
        sa.Column("estado", sa.String(20), nullable=True, server_default="pendiente"),
        sa.Column("urgente", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("urgencia", sa.String(10), nullable=True),
        sa.Column("external_id", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("respondido_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["negocio_id"], ["negocios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mensajes_id", "mensajes", ["id"])
    op.create_index("ix_mensajes_negocio_id", "mensajes", ["negocio_id"])

    # Tabla competidores
    op.create_table(
        "competidores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("negocio_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("fb_page_url", sa.String(300), nullable=True),
        sa.Column("ig_username", sa.String(100), nullable=True),
        sa.Column("gmb_place_id", sa.String(200), nullable=True),
        sa.Column("ultimo_analisis", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["negocio_id"], ["negocios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_competidores_id", "competidores", ["id"])
    op.create_index("ix_competidores_negocio_id", "competidores", ["negocio_id"])

    # Tabla metricas
    op.create_table(
        "metricas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("negocio_id", sa.Integer(), nullable=False),
        sa.Column("plataforma", sa.String(30), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("seguidores", sa.Integer(), nullable=True),
        sa.Column("alcance_organico", sa.Integer(), nullable=True),
        sa.Column("mensajes_recibidos", sa.Integer(), nullable=True),
        sa.Column("mensajes_respondidos", sa.Integer(), nullable=True),
        sa.Column("resenas_positivas", sa.Integer(), nullable=True),
        sa.Column("resenas_negativas", sa.Integer(), nullable=True),
        sa.Column("rating_promedio", sa.Float(), nullable=True),
        sa.Column("posts_publicados", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["negocio_id"], ["negocios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_metricas_id", "metricas", ["id"])
    op.create_index("ix_metricas_negocio_id", "metricas", ["negocio_id"])

    # Tabla suscripciones
    op.create_table(
        "suscripciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("negocio_id", sa.Integer(), nullable=False),
        sa.Column("plan", sa.String(20), nullable=False),
        sa.Column("monto_soles", sa.Float(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=True, server_default="pendiente"),
        sa.Column("fecha_inicio", sa.DateTime(), nullable=True),
        sa.Column("fecha_vencimiento", sa.DateTime(), nullable=True),
        sa.Column("culqi_charge_id", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["negocio_id"], ["negocios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("culqi_charge_id"),
    )
    op.create_index("ix_suscripciones_id", "suscripciones", ["id"])
    op.create_index("ix_suscripciones_negocio_id", "suscripciones", ["negocio_id"])


def downgrade() -> None:
    op.drop_table("suscripciones")
    op.drop_table("metricas")
    op.drop_table("competidores")
    op.drop_table("mensajes")
    op.drop_table("negocios")
