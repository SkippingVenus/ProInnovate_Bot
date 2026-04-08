"""BOT-6: agregar campos Meta faltantes y constraint de deduplicacion

Revision ID: 0002_bot6_meta_fields
Revises: 0001_initial
Create Date: 2026-04-05 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_bot6_meta_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("negocios", sa.Column("fb_page_name", sa.String(length=200), nullable=True))
    op.add_column("negocios", sa.Column("ig_access_token", sa.Text(), nullable=True))

    op.add_column("mensajes", sa.Column("autor_id", sa.String(length=100), nullable=True))
    op.create_unique_constraint(
        "uq_mensajes_plataforma_external_id",
        "mensajes",
        ["plataforma", "external_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_mensajes_plataforma_external_id", "mensajes", type_="unique")
    op.drop_column("mensajes", "autor_id")

    op.drop_column("negocios", "ig_access_token")
    op.drop_column("negocios", "fb_page_name")
