"""Faculty response model for a query."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class FacultyResponse:
    id: UUID
    query_id: UUID
    faculty_id: UUID
    message: str
    created_at: datetime
