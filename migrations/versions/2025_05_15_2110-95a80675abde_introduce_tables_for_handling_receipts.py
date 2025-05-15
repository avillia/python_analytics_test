"""introduce tables for handling receipts

Revision ID: 95a80675abde
Revises: 112f563907ed
Create Date: 2025-05-15 21:10:24.305298

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "95a80675abde"
down_revision: str | None = "112f563907ed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "receipts",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=255),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("is_cashless_payment", sa.Boolean(), nullable=False),
        sa.Column("payment_amount", sa.DECIMAL(2), nullable=False),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "receipt_items",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "receipt_id",
            sa.String(length=255),
            sa.ForeignKey("receipts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("price", sa.DECIMAL(2), nullable=False),
        sa.Column("quantity", sa.DECIMAL(2), nullable=False),
    )

    op.execute(
        """
        INSERT INTO apps_configs (key, value, type) VALUES
          ('delimiter',            '=',                   'str'),
          ('separator',            '-',                   'str'),
          ('thank_you_note',       'Дякуємо за покупку!', 'str'),
          ('cash_label',           'Готівка',             'str'),
          ('cashless_label',       'Картка',              'str'),
          ('total_label',          'СУМА',                'str'),
          ('rest_label',           'Решта',               'str'),
          ('datetime_format',      '%d.%m.%Y %H:%M',      'str');
        """
    )


def downgrade() -> None:
    op.drop_table("receipt_items")
    op.drop_table("receipts")
