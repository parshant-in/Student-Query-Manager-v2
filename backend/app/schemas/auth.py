"""Authentication request and response schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, TypeAdapter, field_validator

from app.core.dev_data import DEV_FACULTY_IDS
from app.schemas.user import UserResponse

email_adapter = TypeAdapter(EmailStr)


def validate_auth_email(value: str) -> str:
    normalized = value.casefold()
    if normalized in DEV_FACULTY_IDS:
        return normalized
    return str(email_adapter.validate_python(value))


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    full_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=10)

    _validate_email = field_validator("email")(validate_auth_email)


class LoginRequest(BaseModel):
    email: str
    password: str

    _validate_email = field_validator("email")(validate_auth_email)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
