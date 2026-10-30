"""Request and response schemas for student queries."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.query import QueryStatus


class FacultyResponseSchema(BaseModel):
    id: UUID
    query_id: UUID
    faculty_id: UUID | None
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: str


class QueryCreateRequest(BaseModel):
    category_id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)

    @field_validator("title", "description")
    @classmethod
    def strip_nonempty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value


class QueryResponse(BaseModel):
    id: UUID
    student_id: UUID
    category_id: UUID
    faculty_id: UUID | None
    title: str
    description: str
    status: QueryStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QueryDetailResponse(QueryResponse):
    responses: list[FacultyResponseSchema]


class FacultyResponseRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)

    @field_validator("message")
    @classmethod
    def strip_nonempty_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message must not be blank")
        return value


class QueryStatusUpdateRequest(BaseModel):
    status: QueryStatus


class FacultyDepartmentUpdateRequest(BaseModel):
    department_id: UUID


class FacultyDepartmentResponse(BaseModel):
    department_id: UUID | None
