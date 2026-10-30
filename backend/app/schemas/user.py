"""Pydantic schemas for User data sent/received over the API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.user import UserRole


class UserResponse(BaseModel):
    """Shape of a user object returned by the API. Never includes password_hash."""

    id: UUID
    email: str
    full_name: str
    role: UserRole
    created_at: datetime
    is_active: bool = True

    model_config = {"from_attributes": True}
