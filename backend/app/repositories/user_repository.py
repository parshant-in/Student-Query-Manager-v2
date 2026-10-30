"""SQLAlchemy-backed user repository."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, text, update
from sqlalchemy.exc import IntegrityError

from app.db.orm_models import PasswordResetAuditRecord, UserRecord
from app.db.session import SessionLocal
from app.models.user import User, UserRole


def _to_domain(record: UserRecord) -> User:
    return User(
        id=record.id,
        email=record.email,
        full_name=record.full_name,
        role=UserRole(record.role),
        password_hash=record.password_hash,
        created_at=record.created_at,
        is_active=record.is_active,
        department_id=record.department_id,
        token_version=record.token_version,
    )


class UserRepository:
    def add(self, user: User) -> None:
        with SessionLocal() as session:
            session.add(
                UserRecord(
                    id=user.id,
                    email=user.email.casefold(),
                    full_name=user.full_name,
                    password_hash=user.password_hash,
                    role=user.role.value,
                    is_active=user.is_active,
                    department_id=user.department_id,
                    token_version=user.token_version,
                    created_at=user.created_at,
                )
            )
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ValueError("User already exists") from exc

    def get_by_email(self, email: str) -> User | None:
        with SessionLocal() as session:
            record = session.scalar(
                select(UserRecord).where(UserRecord.email == email.casefold())
            )
            return _to_domain(record) if record is not None else None

    def get_by_id(self, user_id: UUID) -> User | None:
        with SessionLocal() as session:
            record = session.get(UserRecord, user_id)
            return _to_domain(record) if record is not None else None

    def list_by_role(self, role: UserRole) -> list[User]:
        with SessionLocal() as session:
            records = session.scalars(
                select(UserRecord).where(UserRecord.role == role.value).order_by(UserRecord.email)
            ).all()
            return [_to_domain(record) for record in records]

    def get_department_id(self, user_id: UUID) -> UUID | None:
        with SessionLocal() as session:
            record = session.get(UserRecord, user_id)
            return record.department_id if record is not None else None

    def create_first_admin(self, user: User) -> bool:
        """Create the first administrator while serializing Postgres bootstrap attempts."""
        with SessionLocal() as session:
            if session.bind.dialect.name == "postgresql":
                session.execute(text("SELECT pg_advisory_xact_lock(782347125901)"))
            admins = session.scalar(
                select(func.count()).select_from(UserRecord).where(UserRecord.role == UserRole.admin.value)
            )
            if admins:
                session.rollback()
                return False
            session.add(UserRecord(
                id=user.id, email=user.email.casefold(), full_name=user.full_name,
                password_hash=user.password_hash, role=UserRole.admin.value,
                is_active=True, department_id=None, created_at=user.created_at,
                token_version=user.token_version,
            ))
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ValueError("User already exists") from exc
            return True

    def create_faculty(self, user: User, department_id: UUID) -> None:
        with SessionLocal() as session:
            session.add(UserRecord(
                id=user.id, email=user.email.casefold(), full_name=user.full_name,
                password_hash=user.password_hash, role=UserRole.faculty.value,
                is_active=True, department_id=department_id, created_at=user.created_at,
                token_version=user.token_version,
            ))
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ValueError("User already exists") from exc

    def set_active(self, user_id: UUID, is_active: bool) -> bool:
        with SessionLocal() as session:
            result = session.execute(
                update(UserRecord).where(
                    UserRecord.id == user_id,
                    UserRecord.role == UserRole.faculty.value,
                ).values(is_active=is_active)
            )
            session.commit()
            return result.rowcount == 1

    def set_faculty_department(self, user_id: UUID, department_id: UUID) -> bool:
        with SessionLocal() as session:
            result = session.execute(
                update(UserRecord).where(
                    UserRecord.id == user_id,
                    UserRecord.role == UserRole.faculty.value,
                ).values(department_id=department_id)
            )
            session.commit()
            return result.rowcount == 1

    def reset_password(self, *, user_id: UUID, admin_id: UUID, password_hash: str) -> User | None:
        """Replace a student or faculty password, invalidate their JWTs, and audit the event."""
        with SessionLocal() as session:
            record = session.get(UserRecord, user_id)
            if record is None or record.role not in {UserRole.student.value, UserRole.faculty.value}:
                session.rollback()
                return None
            record.password_hash = password_hash
            record.token_version += 1
            session.add(PasswordResetAuditRecord(
                target_user_id=record.id,
                admin_id=admin_id,
                target_role=record.role,
                created_at=datetime.now(timezone.utc),
            ))
            session.commit()
            return _to_domain(record)
