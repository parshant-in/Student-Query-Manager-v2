"""Allow faculty department membership and atomic query claiming."""

from alembic import op
import sqlalchemy as sa


revision = "20261022_faculty_departments"
down_revision = "5be622018e4b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("department_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_users_department_id_categories",
        "users",
        "categories",
        ["department_id"],
        ["id"],
    )
    op.create_index("ix_users_department_id", "users", ["department_id"])
    # Preserve existing category-to-faculty defaults as initial memberships.
    op.execute(
        sa.text(
            """UPDATE users AS u SET department_id = (
                SELECT c.id FROM categories AS c
                WHERE c.faculty_id = u.id ORDER BY c.name LIMIT 1
            ) WHERE u.role = 'faculty' AND u.department_id IS NULL
            AND EXISTS (SELECT 1 FROM categories AS c WHERE c.faculty_id = u.id)"""
        )
    )
    op.alter_column("queries", "faculty_id", existing_type=sa.Uuid(), nullable=True)


def downgrade() -> None:
    # Restore a legacy category assignee before making faculty_id non-null.
    op.execute(
        sa.text(
            "UPDATE queries SET faculty_id = (SELECT faculty_id FROM categories "
            "WHERE categories.id = queries.category_id) WHERE faculty_id IS NULL"
        )
    )
    op.alter_column("queries", "faculty_id", existing_type=sa.Uuid(), nullable=False)
    op.drop_index("ix_users_department_id", table_name="users")
    op.drop_constraint("fk_users_department_id_categories", "users", type_="foreignkey")
    op.drop_column("users", "department_id")
