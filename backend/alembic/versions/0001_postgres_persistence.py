"""Create PostgreSQL persistence tables."""

from alembic import op
import sqlalchemy as sa


revision = "0001_postgres_persistence"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("faculty_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["faculty_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_categories_faculty_id", "categories", ["faculty_id"])

    op.create_table(
        "queries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("faculty_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('pending', 'solved', 'unsolved')", name="ck_queries_status"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["faculty_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_queries_category_id", "queries", ["category_id"])
    op.create_index("ix_queries_faculty_id", "queries", ["faculty_id"])
    op.create_index("ix_queries_faculty_created", "queries", ["faculty_id", "created_at"])
    op.create_index("ix_queries_student_id", "queries", ["student_id"])
    op.create_index("ix_queries_student_created", "queries", ["student_id", "created_at"])

    op.create_table(
        "responses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("query_id", sa.Uuid(), nullable=False),
        sa.Column("faculty_id", sa.Uuid(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["faculty_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["query_id"], ["queries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_responses_query_id", "responses", ["query_id"])


def downgrade() -> None:
    op.drop_index("ix_responses_query_id", table_name="responses")
    op.drop_table("responses")
    op.drop_index("ix_queries_student_created", table_name="queries")
    op.drop_index("ix_queries_student_id", table_name="queries")
    op.drop_index("ix_queries_faculty_created", table_name="queries")
    op.drop_index("ix_queries_faculty_id", table_name="queries")
    op.drop_index("ix_queries_category_id", table_name="queries")
    op.drop_table("queries")
    op.drop_index("ix_categories_faculty_id", table_name="categories")
    op.drop_table("categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
