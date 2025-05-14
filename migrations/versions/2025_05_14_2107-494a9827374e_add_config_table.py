"""add config table

Revision ID: 494a9827374e
Revises: c8d7ae288b1d
Create Date: 2025-05-14 21:07:21.755757

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "494a9827374e"
down_revision: str | None = "c8d7ae288b1d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "apps_configs",
        sa.Column("key", sa.String(length=32), primary_key=True),
        sa.Column("value", sa.String(length=128), nullable=False),
        sa.Column(
            "type",
            sa.Enum("str", "float", "int", "bool", name="config_value_type"),
            nullable=False,
        ),
    )

    op.execute(
        """
        INSERT INTO apps_configs (key, value, type)
        VALUES ('ACCESS_TOKEN_EXPIRE_MINUTES', '60', 'int')
        """
    )


def downgrade() -> None:
    op.drop_table("apps_configs")
    op.execute("DROP TYPE config_value_type")
