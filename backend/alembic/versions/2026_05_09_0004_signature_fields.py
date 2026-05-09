"""Add signature fields to contract_reviews

Revision ID: 2026_05_09_0004
Revises: 2026_05_09_0003
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "2026_05_09_0004"
down_revision: Union[str, None] = "2026_05_09_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "contract_reviews",
        sa.Column("envelope_id", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "contract_reviews",
        sa.Column("signer_email", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "contract_reviews",
        sa.Column("signature_status", sa.String(length=50), nullable=True),
    )
    op.create_index(
        "ix_contract_reviews_envelope_id",
        "contract_reviews",
        ["envelope_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_contract_reviews_envelope_id", table_name="contract_reviews")
    op.drop_column("contract_reviews", "signature_status")
    op.drop_column("contract_reviews", "signer_email")
    op.drop_column("contract_reviews", "envelope_id")
