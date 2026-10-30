"""Administrator-only account management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.schemas.admin import (
    FacultyAccountResponse,
    FacultyCreateRequest,
    FacultyDepartmentUpdateRequest,
    FacultyStatusUpdateRequest,
    PasswordResetRequest,
)
from app.services.admin_service import DuplicateFacultyEmailError, admin_service

router = APIRouter(prefix="/admin", tags=["administrator"])


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@router.get("/faculty", response_model=list[FacultyAccountResponse])
def list_faculty(_: User = Depends(get_current_admin)) -> list[FacultyAccountResponse]:
    return admin_service.list_faculty()


@router.get("/students", response_model=list[FacultyAccountResponse])
def list_students(_: User = Depends(get_current_admin)) -> list[FacultyAccountResponse]:
    return admin_service.list_students()


@router.post("/users/{user_id}/reset-password", response_model=FacultyAccountResponse)
def reset_user_password(
    user_id: UUID, request: PasswordResetRequest, admin: User = Depends(get_current_admin)
) -> FacultyAccountResponse:
    user = admin_service.reset_user_password(
        user_id=user_id, admin_id=admin.id, new_password=request.new_password
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Student or faculty account not found")
    return user


@router.post("/faculty", response_model=FacultyAccountResponse, status_code=201)
def create_faculty(
    request: FacultyCreateRequest, _: User = Depends(get_current_admin)
) -> FacultyAccountResponse:
    try:
        return admin_service.create_faculty(
            email=str(request.email), full_name=request.full_name,
            password=request.password, department_id=request.department_id,
        )
    except DuplicateFacultyEmailError:
        raise HTTPException(status_code=409, detail="Email is already registered") from None
    except LookupError:
        raise HTTPException(status_code=404, detail="Department not found") from None


@router.patch("/faculty/{faculty_id}/status", response_model=FacultyAccountResponse)
def set_faculty_status(
    faculty_id: UUID, request: FacultyStatusUpdateRequest,
    _: User = Depends(get_current_admin),
) -> FacultyAccountResponse:
    faculty = admin_service.set_faculty_status(faculty_id, request.is_active)
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty account not found")
    return faculty


@router.patch("/faculty/{faculty_id}/department", response_model=FacultyAccountResponse)
def set_faculty_department(
    faculty_id: UUID, request: FacultyDepartmentUpdateRequest,
    _: User = Depends(get_current_admin),
) -> FacultyAccountResponse:
    try:
        faculty = admin_service.set_faculty_department(faculty_id, request.department_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Department not found") from None
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty account not found")
    return faculty
