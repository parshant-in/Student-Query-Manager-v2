"""Business logic for administrator-managed faculty accounts."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import FacultyAccountResponse


class DuplicateFacultyEmailError(Exception):
    pass


class AdminService:
    def __init__(self, users: UserRepository, categories: CategoryRepository) -> None:
        self.users = users
        self.categories = categories

    @staticmethod
    def _response(user: User) -> FacultyAccountResponse:
        return FacultyAccountResponse(
            id=user.id, email=user.email, full_name=user.full_name, role=user.role.value,
            department_id=user.department_id, is_active=user.is_active,
            created_at=user.created_at,
        )

    def list_faculty(self) -> list[FacultyAccountResponse]:
        return [self._response(user) for user in self.users.list_by_role(UserRole.faculty)]

    def list_students(self) -> list[FacultyAccountResponse]:
        return [self._response(user) for user in self.users.list_by_role(UserRole.student)]

    def reset_user_password(self, *, user_id: UUID, admin_id: UUID, new_password: str) -> FacultyAccountResponse | None:
        user = self.users.reset_password(
            user_id=user_id, admin_id=admin_id, password_hash=hash_password(new_password)
        )
        return self._response(user) if user is not None else None

    def create_faculty(
        self, *, email: str, full_name: str, password: str, department_id: UUID
    ) -> FacultyAccountResponse:
        if self.categories.get_by_id(department_id) is None:
            raise LookupError("Department not found")
        email = email.strip().casefold()
        user = User(
            id=uuid4(), email=email, full_name=full_name.strip(), role=UserRole.faculty,
            password_hash=hash_password(password), created_at=datetime.now(timezone.utc),
            department_id=department_id,
        )
        try:
            self.users.create_faculty(user, department_id)
        except ValueError as exc:
            raise DuplicateFacultyEmailError from exc
        return self._response(user)

    def set_faculty_status(self, faculty_id: UUID, is_active: bool) -> FacultyAccountResponse | None:
        if not self.users.set_active(faculty_id, is_active):
            return None
        user = self.users.get_by_id(faculty_id)
        return self._response(user) if user else None

    def set_faculty_department(
        self, faculty_id: UUID, department_id: UUID
    ) -> FacultyAccountResponse | None:
        if self.categories.get_by_id(department_id) is None:
            raise LookupError("Department not found")
        if not self.users.set_faculty_department(faculty_id, department_id):
            return None
        user = self.users.get_by_id(faculty_id)
        return self._response(user) if user else None


admin_service = AdminService(UserRepository(), CategoryRepository())
