"""Student-only query endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.schemas.query import QueryCreateRequest, QueryDetailResponse, QueryResponse
from app.services.query_service import (
    CategoryNotFoundError,
    query_service,
)

router = APIRouter(prefix="/queries", tags=["queries"])


def get_current_student(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.student:
        raise HTTPException(status_code=403, detail="Student role required")
    return current_user


@router.post("", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
def create_query(
    request: QueryCreateRequest,
    current_student: User = Depends(get_current_student),
) -> QueryResponse:
    try:
        return query_service.create_query(
            student_id=current_student.id,
            category_id=request.category_id,
            title=request.title,
            description=request.description,
        )
    except CategoryNotFoundError:
        raise HTTPException(status_code=404, detail="Category not found") from None


@router.get("", response_model=list[QueryResponse])
def list_my_queries(
    current_student: User = Depends(get_current_student),
) -> list[QueryResponse]:
    return query_service.list_student_queries(current_student.id)


@router.get("/{query_id}", response_model=QueryDetailResponse)
def get_my_query(
    query_id: UUID, current_student: User = Depends(get_current_student)
) -> QueryDetailResponse:
    query = query_service.get_student_query(current_student.id, query_id)
    if query is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return query
