"""Document model for uploaded knowledge-base files."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Document:
    id: UUID
    title: str
    filename: str
    file_path: str
    uploaded_by: UUID
    created_at: datetime