"""Business logic for categories and student-owned queries."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.models.query import Category, Query, QueryStatus
from app.models.response import FacultyResponse
from app.repositories.category_repository import CategoryRepository
from app.repositories.query_repository import QueryRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import auth_service


class CategoryNotFoundError(Exception):
    pass


class QueryAlreadyClaimedError(Exception):
    pass


class QueryService:
    def __init__(
        self, categories: CategoryRepository, queries: QueryRepository, users: UserRepository
    ) -> None:
        self.categories = categories
        self.queries = queries
        self.users = users

    def list_categories(self) -> list[Category]:
        return self.categories.list_all()

    def seed_categories(self) -> None:
        self.categories.seed_defaults()

    def create_query(
        self, *, student_id: UUID, category_id: UUID, title: str, description: str
    ) -> Query:
        category = self.categories.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError
        now = datetime.now(timezone.utc)
        query = Query(
            id=uuid4(),
            student_id=student_id,
            category_id=category_id,
            faculty_id=None,
            title=title.strip(),
            description=description.strip(),
            status=QueryStatus.pending,
            created_at=now,
            updated_at=now,
            responses=[],
        )
        self.queries.add(query)
        return query

    def list_student_queries(self, student_id: UUID) -> list[Query]:
        return self.queries.list_for_student(student_id)

    def get_student_query(self, student_id: UUID, query_id: UUID) -> Query | None:
        query = self.queries.get_by_id(query_id)
        if query is None or query.student_id != student_id:
            return None
        return query

    def list_faculty_queries(self, faculty_id: UUID) -> list[Query]:
        department_id = self.users.get_department_id(faculty_id)
        if department_id is None:
            return []
        return self.queries.list_for_faculty_department(faculty_id, department_id)

    def get_faculty_query(self, faculty_id: UUID, query_id: UUID) -> Query | None:
        query = self.queries.get_by_id(query_id)
        if query is None:
            return None
        if query.faculty_id == faculty_id:
            return query
        department_id = self.users.get_department_id(faculty_id)
        if department_id == query.category_id:
            return query
        return None

    def claim_faculty_query(self, faculty_id: UUID, query_id: UUID) -> Query | None:
        department_id = self.users.get_department_id(faculty_id)
        if department_id is None:
            return None
        query = self.queries.get_by_id(query_id)
        if query is None or query.category_id != department_id:
            return None
        if query.faculty_id == faculty_id:
            return query
        if query.faculty_id is not None:
            raise QueryAlreadyClaimedError
        if not self.queries.claim_for_faculty(query_id, faculty_id, department_id):
            latest = self.queries.get_by_id(query_id)
            if latest is not None and latest.faculty_id == faculty_id:
                return latest
            if latest is not None and latest.category_id == department_id:
                raise QueryAlreadyClaimedError
            return None
        return self.queries.get_by_id(query_id)

    def get_faculty_department(self, faculty_id: UUID) -> UUID | None:
        return self.users.get_department_id(faculty_id)

    def add_faculty_response(
        self, *, faculty_id: UUID, query_id: UUID, message: str
    ) -> FacultyResponse | None:
        query = self.get_faculty_query(faculty_id, query_id)
        if query is None or query.faculty_id != faculty_id:
            return None
        response = FacultyResponse(
            id=uuid4(),
            query_id=query.id,
            faculty_id=faculty_id,
            message=message.strip(),
            created_at=datetime.now(timezone.utc),
        )
        query.updated_at = response.created_at
        if not self.queries.add_response(response, query_updated_at=query.updated_at):
            return None
        return response

    def update_status(
        self, *, faculty_id: UUID, query_id: UUID, status: QueryStatus
    ) -> Query | None:
        query = self.get_faculty_query(faculty_id, query_id)
        if query is None or query.faculty_id != faculty_id:
            return None
        query.status = status
        query.updated_at = datetime.now(timezone.utc)
        if not self.queries.update_status(query, faculty_id=faculty_id):
            return None
        return self.queries.get_by_id(query_id)


query_service = QueryService(CategoryRepository(), QueryRepository(), auth_service.users)
