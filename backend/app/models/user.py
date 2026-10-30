"""Basic User model. No database yet, just a plain Python representation."""

from datetime import datetime
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    student = "student"
    faculty = "faculty"
    admin = "admin"


class User:
    """Represents a user of the system."""

    def __init__(
        self,
        id: UUID,
        email: str,
        full_name: str,
        role: UserRole,
        password_hash: str,
        created_at: datetime,
        is_active: bool = True,
        department_id: UUID | None = None,
        token_version: int = 0,
    ) -> None:
        self.id = id
        self.email = email
        self.full_name = full_name
        self.role = role
        self.password_hash = password_hash
        self.created_at = created_at
        self.is_active = is_active
        self.department_id = department_id
        self.token_version = token_version
