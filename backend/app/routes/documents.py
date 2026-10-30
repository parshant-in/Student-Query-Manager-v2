"""API routes for knowledge-base documents."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.services.document_service import (
    DocumentDeletionError,
    DocumentNotFoundError,
    DocumentRollbackError,
    DocumentUploadError,
    document_service,
)

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_uploader(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in {UserRole.faculty, UserRole.admin}:
        raise HTTPException(
            status_code=403,
            detail="Faculty or admin role required",
        )

    return current_user


@router.post("", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str = "",
    current_user: User = Depends(get_document_uploader),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    content = await file.read()

    try:
        document = document_service.create_document(
            title=title or file.filename,
            filename=file.filename,
            content=content,
            uploaded_by=current_user.id,
            role=current_user.role,
        )
    except DocumentRollbackError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
    except DocumentUploadError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return document


@router.get("")
def list_documents(
    current_user: User = Depends(get_current_user),
):
    return document_service.documents.list_all()


@router.get("/{document_id}")
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
):
    document = document_service.documents.get_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_document_uploader),
):
    try:
        document_service.delete_document(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except DocumentDeletionError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return {
        "message": "Document deleted successfully"
    }
