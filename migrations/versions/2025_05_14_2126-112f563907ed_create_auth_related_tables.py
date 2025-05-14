"""create auth-related tables

Revision ID: 112f563907ed
Revises: 494a9827374e
Create Date: 2025-05-14 21:26:01.139233

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "112f563907ed"
down_revision: str | None = "494a9827374e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("login", sa.String(length=50), unique=True, nullable=False),
        sa.Column("email", sa.String(length=255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column("name", sa.String(length=50), unique=True, nullable=False),
    )

    op.create_table(
        "users_roles",
        sa.Column(
            "user_id",
            sa.String(length=12),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            sa.String(length=255),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    allowed_method_enum = sa.Enum(
        "GET", "POST", "PUT", "PATCH", "DELETE", "*", name="allowed_method"
    )

    op.create_table(
        "accesses",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column(
            "role_id",
            sa.String(length=255),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("route_url", sa.String(length=200), nullable=False),
        sa.Column("allowed_method", allowed_method_enum, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("accesses")
    op.execute("DROP TYPE allowed_method")
    op.drop_table("users_roles")
    op.drop_table("roles")
    op.drop_table("users")
