"""init db

Revision ID: c8d7ae288b1d
Revises:
Create Date: 2025-05-10 15:10:00.923518

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8d7ae288b1d"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Upgrade schema.
    Initialise 'products', 'tags' and associate 'products_tags' tables to db.
    """
    op.create_table(
        "products",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("price", sa.Float(), nullable=False),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=True, server_default=None),
    )

    op.create_table(
        "products_tags",
        sa.Column(
            "product_id",
            sa.String(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "tag_id",
            sa.String(),
            sa.ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    """
    Downgrade schema.
    Drop in reverse order to respect FKs.
    """
    op.drop_table("products_tags")
    op.drop_table("tags")
    op.drop_table("products")
