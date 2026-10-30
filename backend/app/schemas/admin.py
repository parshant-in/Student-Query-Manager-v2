"""Administrator-only account management schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class FacultyCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=10)
    department_id: UUID

    @field_validator("full_name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be blank")
        return value


class FacultyStatusUpdateRequest(BaseModel):
    is_active: bool


class PasswordResetRequest(BaseModel):
    new_password: str = Field(min_length=10)

    @field_validator("new_password")
    @classmethod
    def require_nonblank_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password must not be blank")
        return value


class FacultyDepartmentUpdateRequest(BaseModel):
    department_id: UUID


class FacultyAccountResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    department_id: UUID | None
    is_active: bool
    created_at: datetime
