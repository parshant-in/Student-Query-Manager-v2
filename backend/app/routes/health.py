"""Health check route to confirm the API is running."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok", "service": "student-query-manager"}
