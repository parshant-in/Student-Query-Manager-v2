"""SQLAlchemy-backed repository for student queries and faculty responses."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.orm import selectinload

from app.db.orm_models import QueryRecord, ResponseRecord
from app.db.session import SessionLocal
from app.models.query import Query, QueryStatus
from app.models.response import FacultyResponse


def _response_to_domain(record: ResponseRecord) -> FacultyResponse:
    return FacultyResponse(
        id=record.id,
        query_id=record.query_id,
        faculty_id=record.faculty_id,
        message=record.message,
        created_at=record.created_at,
    )


def _to_domain(record: QueryRecord) -> Query:
    return Query(
        id=record.id,
        student_id=record.student_id,
        category_id=record.category_id,
        faculty_id=record.faculty_id,
        title=record.title,
        description=record.description,
        status=QueryStatus(record.status),
        created_at=record.created_at,
        updated_at=record.updated_at,
        responses=[_response_to_domain(response) for response in record.responses],
    )


class QueryRepository:
    def add(self, query: Query) -> None:
        with SessionLocal() as session:
            record = QueryRecord(
                id=query.id,
                student_id=query.student_id,
                category_id=query.category_id,
                faculty_id=query.faculty_id,
                title=query.title,
                description=query.description,
                status=query.status.value,
                created_at=query.created_at,
                updated_at=query.updated_at,
            )
            session.add(record)
            session.commit()

    def get_by_id(self, query_id: UUID) -> Query | None:
        with SessionLocal() as session:
            record = session.scalar(
                select(QueryRecord)
                .options(selectinload(QueryRecord.responses))
                .where(QueryRecord.id == query_id)
            )
            return _to_domain(record) if record is not None else None

    def list_for_student(self, student_id: UUID) -> list[Query]:
        with SessionLocal() as session:
            records = session.scalars(
                select(QueryRecord)
                .options(selectinload(QueryRecord.responses))
                .where(QueryRecord.student_id == student_id)
                .order_by(QueryRecord.created_at.desc())
            ).all()
            return [_to_domain(record) for record in records]

    def list_for_faculty_department(self, faculty_id: UUID, department_id: UUID) -> list[Query]:
        with SessionLocal() as session:
            records = session.scalars(
                select(QueryRecord)
                .options(selectinload(QueryRecord.responses))
                .where(
                    or_(
                        QueryRecord.faculty_id == faculty_id,
                        QueryRecord.category_id == department_id,
                    )
                )
                .order_by(QueryRecord.created_at.desc())
            ).all()
            return [_to_domain(record) for record in records]

    def claim_for_faculty(self, query_id: UUID, faculty_id: UUID, department_id: UUID) -> bool:
        """Atomically claim an unassigned query in a faculty member's department."""
        with SessionLocal() as session:
            result = session.execute(
                update(QueryRecord)
                .where(
                    QueryRecord.id == query_id,
                    QueryRecord.category_id == department_id,
                    QueryRecord.faculty_id.is_(None),
                )
                .values(faculty_id=faculty_id)
            )
            session.commit()
            return result.rowcount == 1

    def add_response(
        self, response: FacultyResponse, *, query_updated_at: datetime
    ) -> bool:
        with SessionLocal() as session:
            result = session.execute(
                update(QueryRecord)
                .where(
                    QueryRecord.id == response.query_id,
                    QueryRecord.faculty_id == response.faculty_id,
                )
                .values(updated_at=query_updated_at)
            )
            if result.rowcount != 1:
                session.rollback()
                return False
            session.add(
                ResponseRecord(
                    id=response.id,
                    query_id=response.query_id,
                    faculty_id=response.faculty_id,
                    message=response.message,
                    created_at=response.created_at,
                )
            )
            session.commit()
            return True

    def update_status(self, query: Query, *, faculty_id: UUID) -> bool:
        with SessionLocal() as session:
            result = session.execute(
                update(QueryRecord)
                .where(
                    QueryRecord.id == query.id,
                    QueryRecord.faculty_id == faculty_id,
                )
                .values(status=query.status.value, updated_at=query.updated_at)
            )
            if result.rowcount != 1:
                session.rollback()
                return False
            session.commit()
            return True
