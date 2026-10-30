"""Authentication business logic."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.core.dev_data import DEV_FACULTY_IDS
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def register(
        self, *, email: str, full_name: str, password: str
    ) -> tuple[str, User]:
        normalized_email = email.strip().casefold()
        if self.users.get_by_email(normalized_email) is not None:
            raise DuplicateEmailError

        user = User(
            id=uuid4(),
            email=normalized_email,
            full_name=full_name,
            role=UserRole.student,
            password_hash=hash_password(password),
            created_at=datetime.now(timezone.utc),
        )
        try:
            self.users.add(user)
        except ValueError as exc:
            raise DuplicateEmailError from exc
        return create_access_token(str(user.id), user.role, user.token_version), user

    def login(self, *, email: str, password: str) -> tuple[str, User]:
        user = self.users.get_by_email(email.strip().casefold())
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError
        return create_access_token(str(user.id), user.role, user.token_version), user

    def get_user(self, user_id: UUID) -> User | None:
        user = self.users.get_by_id(user_id)
        return user if user is not None and user.is_active else None

    def create_first_admin(self, *, email: str, full_name: str, password: str) -> bool:
        email = email.strip().casefold()
        user = User(
            id=uuid4(), email=email, full_name=full_name.strip(), role=UserRole.admin,
            password_hash=hash_password(password), created_at=datetime.now(timezone.utc),
        )
        return self.users.create_first_admin(user)

    def seed_development_faculty(self) -> None:
        """Create deterministic fake faculty accounts for local development."""
        if not settings.DEV_FACULTY_PASSWORD:
            raise RuntimeError(
                "Set DEV_FACULTY_PASSWORD in the local environment to seed faculty users"
            )
        if len(settings.DEV_FACULTY_PASSWORD) < 10:
            raise RuntimeError("DEV_FACULTY_PASSWORD must be at least 10 characters")
        for email, user_id in DEV_FACULTY_IDS.items():
            existing = self.users.get_by_id(user_id)
            if existing is not None:
                continue
            existing = self.users.get_by_email(email)
            if existing is not None:
                raise RuntimeError(f"Development faculty email is already used: {email}")
            user = User(
                id=user_id,
                email=email,
                full_name=email.split(".")[0].title() + " Faculty (Development)",
                role=UserRole.faculty,
                password_hash=hash_password(settings.DEV_FACULTY_PASSWORD),
                created_at=datetime.now(timezone.utc),
            )
            self.users.add(user)


auth_service = AuthService(UserRepository())
