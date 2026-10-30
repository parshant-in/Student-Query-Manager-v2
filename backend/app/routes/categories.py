"""Available query categories."""

from fastapi import APIRouter

from app.schemas.query import CategoryResponse
from app.services.query_service import query_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories() -> list[CategoryResponse]:
    return query_service.list_categories()
