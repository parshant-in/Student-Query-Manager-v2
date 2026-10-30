"""SQLAlchemy-backed document repository."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.db.orm_models import DocumentRecord
from app.db.session import SessionLocal
from app.models.document import Document


def _to_domain(record: DocumentRecord) -> Document:
    return Document(
        id=record.id,
        title=record.title,
        filename=record.filename,
        file_path=record.file_path,
        uploaded_by=record.uploaded_by,
        created_at=record.created_at,
    )


class DocumentRepository:
    def create(
        self,
        *,
        title: str,
        filename: str,
        file_path: str,
        uploaded_by: UUID,
    ) -> Document:
        with SessionLocal() as session:
            record = DocumentRecord(
                title=title,
                filename=filename,
                file_path=file_path,
                uploaded_by=uploaded_by,
                created_at=datetime.now(timezone.utc),
            )

            session.add(record)
            session.commit()
            session.refresh(record)

            return _to_domain(record)

    def list_all(self) -> list[Document]:
        with SessionLocal() as session:
            records = session.scalars(
                select(DocumentRecord).order_by(DocumentRecord.created_at.desc())
            ).all()

            return [_to_domain(record) for record in records]

    def get_by_id(self, document_id: UUID) -> Document | None:
        with SessionLocal() as session:
            record = session.get(DocumentRecord, document_id)

            return _to_domain(record) if record is not None else None

    def delete(self, document_id: UUID) -> bool:
        with SessionLocal() as session:
            record = session.get(DocumentRecord, document_id)

            if record is None:
                return False

            session.delete(record)
            session.commit()

            return True