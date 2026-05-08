"""Initial migration

Revision ID: 2026_05_08_0001
Revises:
Create Date: 2026-05-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2026_05_08_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contract_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("contract_text", sa.Text(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contract_reviews")),
    )

    op.create_table(
        "clause_findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_review_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("clause_text", sa.Text(), nullable=False),
        sa.Column("clause_type", sa.String(length=100), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="low"),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contract_review_id"], ["contract_reviews.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clause_findings")),
    )
    op.create_index(
        op.f("ix_clause_findings_contract_review_id"),
        "clause_findings",
        ["contract_review_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_clause_findings_contract_review_id"), table_name="clause_findings")
    op.drop_table("clause_findings")
    op.drop_table("contract_reviews")
