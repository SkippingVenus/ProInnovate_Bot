"""Create facebook_pages table for storing multiple pages per business

Revision ID: 0003_create_facebook_pages
Revises: 0002_bot6_meta_fields
Create Date: 2026-05-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_create_facebook_pages"
down_revision = "0002_bot6_meta_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "facebook_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("fb_page_id", sa.String(length=100), nullable=False),
        sa.Column("fb_page_name", sa.String(length=200), nullable=False),
        sa.Column("fb_access_token", sa.Text(), nullable=False),
        sa.Column("instagram_account_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["business_id"], ["negocios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_facebook_pages_business_id"), "facebook_pages", ["business_id"])
    op.create_index(op.f("ix_facebook_pages_fb_page_id"), "facebook_pages", ["fb_page_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_facebook_pages_fb_page_id"), table_name="facebook_pages")
    op.drop_index(op.f("ix_facebook_pages_business_id"), table_name="facebook_pages")
    op.drop_table("facebook_pages")
