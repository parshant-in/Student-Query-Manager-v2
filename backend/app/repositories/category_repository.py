"""SQLAlchemy-backed category repository and idempotent development seeding."""

from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import select

from app.core.dev_data import DEFAULT_CATEGORIES, DEV_FACULTY_IDS
from app.db.orm_models import CategoryRecord, UserRecord
from app.db.session import SessionLocal
from app.models.query import Category
from app.models.user import UserRole


def _to_domain(record: CategoryRecord) -> Category:
    return Category(
        id=record.id,
        name=record.name,
        description=record.description,
        responsible_faculty_id=record.faculty_id,
    )


class CategoryRepository:
    def seed_defaults(self) -> None:
        """Insert or refresh the known development categories without duplicates."""
        with SessionLocal() as session:
            for name, description, faculty_email in DEFAULT_CATEGORIES:
                faculty_id = DEV_FACULTY_IDS[faculty_email]
                faculty = session.get(UserRecord, faculty_id)
                if faculty is None or faculty.role != UserRole.faculty.value:
                    raise RuntimeError(f"Seed faculty is missing for category {name}")

                category = session.scalar(
                    select(CategoryRecord).where(CategoryRecord.name == name)
                )
                if category is None:
                    category = CategoryRecord(
                        id=uuid5(NAMESPACE_URL, f"student-query-manager/category/{name.casefold()}"),
                        name=name,
                        description=description,
                        faculty_id=faculty_id,
                    )
                    session.add(category)
                else:
                    category.description = description
                    category.faculty_id = faculty_id
                if faculty.department_id is None:
                    faculty.department_id = category.id
            session.commit()

    def list_all(self) -> list[Category]:
        with SessionLocal() as session:
            records = session.scalars(
                select(CategoryRecord).order_by(CategoryRecord.name)
            ).all()
            return [_to_domain(record) for record in records]

    def get_by_id(self, category_id: UUID) -> Category | None:
        with SessionLocal() as session:
            record = session.get(CategoryRecord, category_id)
            return _to_domain(record) if record is not None else None
