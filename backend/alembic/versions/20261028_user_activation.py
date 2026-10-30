"""Add account activation flag for faculty access control."""

from alembic import op
import sqlalchemy as sa


revision = "20261028_user_activation"
down_revision = "20261022_faculty_departments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("users", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "is_active")
