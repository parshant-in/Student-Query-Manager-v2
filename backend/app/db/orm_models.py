"""SQLAlchemy persistence models, separate from API/domain models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, server_default="true")
    token_version: Mapped[int] = mapped_column(default=0, nullable=False, server_default="0")
    department_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    student_queries: Mapped[list["QueryRecord"]] = relationship(
        back_populates="student", foreign_keys="QueryRecord.student_id"
    )
    faculty_queries: Mapped[list["QueryRecord"]] = relationship(
        back_populates="faculty", foreign_keys="QueryRecord.faculty_id"
    )
    faculty_categories: Mapped[list["CategoryRecord"]] = relationship(
        back_populates="faculty", foreign_keys="CategoryRecord.faculty_id"
    )
    faculty_responses: Mapped[list["ResponseRecord"]] = relationship(
        back_populates="faculty"
    )
    password_reset_events: Mapped[list["PasswordResetAuditRecord"]] = relationship(
        back_populates="target_user", foreign_keys="PasswordResetAuditRecord.target_user_id"
    )
    password_resets_performed: Mapped[list["PasswordResetAuditRecord"]] = relationship(
        back_populates="admin", foreign_keys="PasswordResetAuditRecord.admin_id"
    )


class PasswordResetAuditRecord(Base):
    __tablename__ = "password_reset_audit_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    target_user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    admin_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    target_role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    target_user: Mapped[UserRecord] = relationship(back_populates="password_reset_events", foreign_keys=[target_user_id])
    admin: Mapped[UserRecord] = relationship(back_populates="password_resets_performed", foreign_keys=[admin_id])


class CategoryRecord(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    faculty_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    faculty: Mapped[UserRecord] = relationship(
        back_populates="faculty_categories", foreign_keys=[faculty_id]
    )
    queries: Mapped[list["QueryRecord"]] = relationship(back_populates="category")


class QueryRecord(Base):
    __tablename__ = "queries"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'solved', 'unsolved')", name="ck_queries_status"
        ),
        Index("ix_queries_student_created", "student_id", "created_at"),
        Index("ix_queries_faculty_created", "faculty_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    category_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("categories.id"), nullable=False, index=True
    )
    faculty_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    student: Mapped[UserRecord] = relationship(
        back_populates="student_queries", foreign_keys=[student_id]
    )
    faculty: Mapped[UserRecord | None] = relationship(
        back_populates="faculty_queries", foreign_keys=[faculty_id]
    )
    category: Mapped[CategoryRecord] = relationship(back_populates="queries")
    responses: Mapped[list["ResponseRecord"]] = relationship(
        back_populates="query", order_by="ResponseRecord.created_at", cascade="all, delete-orphan"
    )


class ResponseRecord(Base):
    __tablename__ = "responses"
    __table_args__ = (Index("ix_responses_query_id", "query_id"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    query_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("queries.id"), nullable=False
    )
    faculty_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    query: Mapped[QueryRecord] = relationship(back_populates="responses")
    faculty: Mapped[UserRecord] = relationship(back_populates="faculty_responses")

class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    uploaded_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    uploader: Mapped[UserRecord] = relationship()
