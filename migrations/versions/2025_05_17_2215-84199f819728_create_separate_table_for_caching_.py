"""create separate table for caching receipts.txt

Revision ID: 84199f819728
Revises: 6660ffcd007c
Create Date: 2025-05-17 22:15:42.699440

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "84199f819728"
down_revision: str | None = "6660ffcd007c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "txt_receipt_cache",
        sa.Column(
            "receipt_id",
            sa.String(length=255),
            sa.ForeignKey("receipts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "config_str",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "txt",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "creation_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("txt_receipt_cache")
