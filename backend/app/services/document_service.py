"""Business logic for uploaded knowledge-base documents."""

from pathlib import Path
from uuid import UUID

from app.models.document import Document
from app.models.user import UserRole
from app.repositories.document_repository import DocumentRepository
from app.services.document_ingestion_service import (
    DocumentIngestionError,
    DocumentIngestionService,
    document_ingestion_service,
)
from app.storage.local_storage import LocalDocumentStorage
from app.services.vector_store import VectorStore, vector_store


class DocumentUploadError(Exception):
    pass


class DocumentRollbackError(DocumentUploadError):
    """Upload failed and cleanup could not restore a consistent state."""


class DocumentNotFoundError(Exception):
    pass


class DocumentDeletionError(Exception):
    """Document cleanup failed; retry may be needed to finish deletion."""


class DocumentService:
    def __init__(
        self,
        documents: DocumentRepository,
        storage: LocalDocumentStorage,
        ingestion: DocumentIngestionService,
        vectors: VectorStore,
    ) -> None:
        self.documents = documents
        self.storage = storage
        self.ingestion = ingestion
        self.vectors = vectors

    def can_upload(self, role: UserRole) -> bool:
        return role in {UserRole.faculty, UserRole.admin}

    def validate_file_type(self, filename: str) -> None:
        extension = filename.lower().rsplit(".", 1)[-1]

        if extension not in {"pdf", "txt"}:
            raise DocumentUploadError(
                "Only PDF and TXT files are supported."
            )

    def create_document(
        self,
        *,
        title: str,
        filename: str,
        content: bytes,
        uploaded_by: UUID,
        role: UserRole,
    ) -> Document:
        if not self.can_upload(role):
            raise DocumentUploadError(
                "Students are not allowed to upload documents."
            )

        self.validate_file_type(filename)

        saved_path = self.storage.save(filename, content)
        try:
            document = self.documents.create(
                title=title.strip(),
                filename=filename,
                file_path=str(saved_path),
                uploaded_by=uploaded_by,
            )
        except Exception as exc:
            try:
                self.storage.delete(saved_path)
            except Exception as cleanup_exc:
                raise DocumentRollbackError(
                    "Document metadata creation failed and the stored file could not be cleaned up."
                ) from cleanup_exc
            raise DocumentUploadError("Could not register the uploaded document.") from exc

        try:
            self.ingestion.ingest_document(document.id)
        except DocumentIngestionError as exc:
            # Ingestion can fail after Chroma has accepted part of an upsert.
            # Remove chunks first; keep the file and DB row if that cleanup fails.
            try:
                self.vectors.delete_document(document.id)
            except Exception as cleanup_exc:
                raise DocumentRollbackError(
                    "Ingestion failed and vector cleanup could not complete; the document record and file were retained."
                ) from cleanup_exc
            try:
                self.storage.delete(saved_path)
                if not self.documents.delete(document.id):
                    raise RuntimeError("Document metadata could not be removed")
            except Exception as cleanup_exc:
                raise DocumentRollbackError(
                    "Ingestion failed and rollback could not complete; retry document cleanup."
                ) from cleanup_exc

            raise DocumentUploadError(
                f"Document ingestion failed: {exc}"
            ) from exc

        return document


    def delete_document(self, document_id: UUID) -> None:
        document = self.documents.get_by_id(document_id)

        if document is None:
            raise DocumentNotFoundError("Document not found.")

        # Chunks carry this stable UUID in their metadata. Remove them first so
        # failed vector cleanup leaves the file and database row retryable.
        try:
            self.vectors.delete_document(document_id)
        except Exception as exc:
            raise DocumentDeletionError(
                "Vector cleanup failed; the document file and record were retained."
            ) from exc

        try:
            self.storage.delete(Path(document.file_path))
            if not self.documents.delete(document_id):
                raise RuntimeError("Document metadata could not be removed")
        except Exception as exc:
            raise DocumentDeletionError(
                "Document cleanup could not be completed. Retry the deletion."
            ) from exc


document_service = DocumentService(
    documents=DocumentRepository(),
    storage=LocalDocumentStorage(Path("storage/documents")),
    ingestion=document_ingestion_service,
    vectors=vector_store,
)
