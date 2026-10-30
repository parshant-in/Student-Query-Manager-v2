"""Add JWT revocation version and password-reset audit records."""

from alembic import op
import sqlalchemy as sa


revision = "20261030_password_reset_security"
down_revision = "20261028_user_activation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("users", "token_version", server_default=None)
    op.create_table(
        "password_reset_audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("target_user_id", sa.Uuid(), nullable=False),
        sa.Column("admin_id", sa.Uuid(), nullable=False),
        sa.Column("target_role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_password_reset_audit_events_target_user_id", "password_reset_audit_events", ["target_user_id"])
    op.create_index("ix_password_reset_audit_events_admin_id", "password_reset_audit_events", ["admin_id"])


def downgrade() -> None:
    op.drop_index("ix_password_reset_audit_events_admin_id", table_name="password_reset_audit_events")
    op.drop_index("ix_password_reset_audit_events_target_user_id", table_name="password_reset_audit_events")
    op.drop_table("password_reset_audit_events")
    op.drop_column("users", "token_version")
