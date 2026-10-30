"""Entry point for the Student Query Manager API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.routes import admin, auth, categories, documents, faculty, health, queries, rag
from app.services.auth_service import auth_service
from app.services.query_service import query_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.APP_ENV == "development":
        auth_service.seed_development_faculty()
        query_service.seed_categories()
    yield

app = FastAPI(
    title="Student Query Manager API",
    description="Backend API for managing student academic queries.",
    version="1.0.0",
    lifespan=lifespan,
)

# All routes in health.py are prefixed with /api
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(queries.router, prefix="/api")
app.include_router(faculty.router, prefix="/api")
app.include_router(faculty.department_router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
