"""Faculty workflow for assigned student queries."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.schemas.query import (
    FacultyDepartmentResponse,
    FacultyResponseRequest,
    FacultyResponseSchema,
    QueryDetailResponse,
    QueryResponse,
    QueryStatusUpdateRequest,
)
from app.services.query_service import QueryAlreadyClaimedError, query_service

router = APIRouter(prefix="/faculty/queries", tags=["faculty"])
department_router = APIRouter(prefix="/faculty/department", tags=["faculty"])


def get_current_faculty(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.faculty:
        raise HTTPException(status_code=403, detail="Faculty role required")
    return current_user


@department_router.get("", response_model=FacultyDepartmentResponse)
def get_department(faculty: User = Depends(get_current_faculty)) -> FacultyDepartmentResponse:
    return FacultyDepartmentResponse(
        department_id=query_service.get_faculty_department(faculty.id)
    )


@router.get("", response_model=list[QueryResponse])
def list_assigned_queries(
    faculty: User = Depends(get_current_faculty),
) -> list[QueryResponse]:
    return query_service.list_faculty_queries(faculty.id)


@router.get("/{query_id}", response_model=QueryDetailResponse)
def get_assigned_query(
    query_id: UUID, faculty: User = Depends(get_current_faculty)
) -> QueryDetailResponse:
    query = query_service.get_faculty_query(faculty.id, query_id)
    if query is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return query


@router.post("/{query_id}/claim", response_model=QueryResponse)
def claim_query(
    query_id: UUID, faculty: User = Depends(get_current_faculty)
) -> QueryResponse:
    try:
        query = query_service.claim_faculty_query(faculty.id, query_id)
    except QueryAlreadyClaimedError:
        raise HTTPException(status_code=409, detail="This query has already been claimed") from None
    if query is None:
        raise HTTPException(status_code=404, detail="Query not found in your department")
    return query


@router.post("/{query_id}/response", response_model=FacultyResponseSchema, status_code=201)
def add_response(
    query_id: UUID,
    request: FacultyResponseRequest,
    faculty: User = Depends(get_current_faculty),
) -> FacultyResponseSchema:
    response = query_service.add_faculty_response(
        faculty_id=faculty.id, query_id=query_id, message=request.message
    )
    if response is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return response


@router.patch("/{query_id}/status", response_model=QueryResponse)
def update_query_status(
    query_id: UUID,
    request: QueryStatusUpdateRequest,
    faculty: User = Depends(get_current_faculty),
) -> QueryResponse:
    query = query_service.update_status(
        faculty_id=faculty.id, query_id=query_id, status=request.status
    )
    if query is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return query
