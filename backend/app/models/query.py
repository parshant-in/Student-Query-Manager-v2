"""In-memory query and category models."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from app.models.response import FacultyResponse


class QueryStatus(str, Enum):
    pending = "pending"
    solved = "solved"
    unsolved = "unsolved"


@dataclass
class Category:
    id: UUID
    name: str
    description: str
    responsible_faculty_id: UUID


@dataclass
class Query:
    id: UUID
    student_id: UUID
    category_id: UUID
    faculty_id: UUID | None
    title: str
    description: str
    status: QueryStatus
    created_at: datetime
    updated_at: datetime
    responses: list[FacultyResponse]
