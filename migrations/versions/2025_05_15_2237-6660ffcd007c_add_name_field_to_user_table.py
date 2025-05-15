"""add name field to user table

Revision ID: 6660ffcd007c
Revises: 95a80675abde
Create Date: 2025-05-15 22:37:00.807403

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6660ffcd007c"
down_revision: str | None = "95a80675abde"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "name")
