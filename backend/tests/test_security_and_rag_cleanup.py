from __future__ import annotations

import tempfile
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch

from pydantic import ValidationError

from app.models.document import Document
from app.models.user import User, UserRole
from app.routes.auth import register
from app.schemas.auth import RegisterRequest
from app.services.document_ingestion_service import DocumentIngestionError, DocumentIngestionService
from app.services.document_service import DocumentDeletionError, DocumentService, DocumentUploadError
from app.services.auth_service import AuthService
from app.services.rag_service import NO_CONTEXT_ANSWER, RagService
from app.services.retrieval_service import RetrievalService
from app.services.text_extraction_service import TextExtractionService
from app.services.chunking_service import ChunkingService
from app.services.vector_store import VectorStore


@contextmanager
def isolated_vector_store(path: str | Path):
    store = VectorStore(path)
    try:
        yield store
    finally:
        store.close()


class InMemoryDocuments:
    def __init__(self, document: Document | None = None, calls: list[str] | None = None) -> None:
        self.document = document
        self.deleted: list[object] = []
        self.calls = calls

    def get_by_id(self, document_id):
        if self.document and self.document.id == document_id:
            return self.document
        return None

    def delete(self, document_id):
        if self.calls is not None:
            self.calls.append("metadata")
        self.deleted.append(document_id)
        if self.document and self.document.id == document_id:
            self.document = None
            return True
        return False

    def create(self, *, title, filename, file_path, uploaded_by):
        if self.calls is not None:
            self.calls.append("metadata-create")
        self.document = Document(uuid4(), title, filename, file_path, uploaded_by, datetime.now(timezone.utc))
        return self.document


class InMemoryUsers:
    def __init__(self) -> None:
        self.user = None

    def get_by_email(self, _email):
        return self.user

    def add(self, user):
        self.user = user


class FakeStorage:
    def __init__(self, calls: list[str], fail: bool = False) -> None:
        self.calls = calls
        self.fail = fail

    def save(self, filename: str, _content: bytes) -> Path:
        return Path(filename)

    def delete(self, _path: Path) -> None:
        self.calls.append("file")
        if self.fail:
            raise OSError("file cleanup failed")


class FakeVectors:
    def __init__(self, calls: list[str], fail: bool = False) -> None:
        self.calls = calls
        self.fail = fail

    def delete_document(self, _document_id) -> None:
        self.calls.append("vectors")
        if self.fail:
            raise RuntimeError("vector cleanup failed")


class FailedIngestion:
    def ingest_document(self, _document_id) -> int:
        raise DocumentIngestionError("simulated ingestion failure")


class FixedEmbeddings:
    def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in chunks]

    def embed_query(self, _question: str) -> list[float]:
        return [1.0, 0.0, 0.0]


class CapturingLlm:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate_answer(self, *, question: str, context: str) -> str:
        self.calls.append((question, context))
        return "Grounded answer"


class SecurityAndRagCleanupTests(unittest.TestCase):
    def test_public_registration_rejects_role_and_route_assigns_student(self) -> None:
        data = {
            "email": "new.student@example.edu",
            "full_name": "New Student",
            "password": "long-enough-password",
        }
        request = RegisterRequest(**data)
        service = AuthService(InMemoryUsers())
        _, service_user = service.register(**data)
        self.assertEqual(service_user.role, UserRole.student)
        created_user = User(
            id=uuid4(),
            email=request.email,
            full_name=request.full_name,
            role=UserRole.student,
            password_hash="not-used-in-test",
            created_at=datetime.now(timezone.utc),
        )
        with patch("app.routes.auth.auth_service.register", return_value=("test-token", created_user)) as register_mock:
            result = register(request)
        self.assertEqual(result.user.role, UserRole.student)
        self.assertNotIn("role", register_mock.call_args.kwargs)
        with self.assertRaises(ValidationError):
            RegisterRequest(**data, role="admin")
        with self.assertRaises(ValidationError):
            RegisterRequest(**data, role="faculty")

    def test_vector_delete_is_document_scoped_and_safe_without_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as path:
            with isolated_vector_store(path) as vectors:
                first_id, second_id, empty_id = uuid4(), uuid4(), uuid4()
                vectors.add_document_chunks(
                    document_id=first_id,
                    chunks=["first document secret"],
                    embeddings=[[1.0, 0.0, 0.0]],
                    filename="first.txt",
                    title="First",
                )
                vectors.add_document_chunks(
                    document_id=second_id,
                    chunks=["second document policy"],
                    embeddings=[[1.0, 0.0, 0.0]],
                    filename="second.txt",
                    title="Second",
                )

                vectors.delete_document(empty_id)
                vectors.delete_document(first_id)
                vectors.delete_document(first_id)
                remaining = vectors.search_similar([1.0, 0.0, 0.0], limit=10)

        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["text"], "second document policy")
        self.assertEqual(remaining[0]["metadata"]["document_id"], str(second_id))

    def test_document_service_cleans_vectors_before_file_and_metadata(self) -> None:
        document = Document(uuid4(), "Guide", "guide.txt", "guide.txt", uuid4(), datetime.now(timezone.utc))
        calls: list[str] = []
        documents = InMemoryDocuments(document, calls)
        storage = FakeStorage(calls)
        vectors = FakeVectors(calls)
        service = DocumentService(documents, storage, ingestion=object(), vectors=vectors)

        service.delete_document(document.id)

        self.assertEqual(calls, ["vectors", "file", "metadata"])
        self.assertIsNone(documents.document)

    def test_vector_cleanup_failure_keeps_file_and_record_for_retry(self) -> None:
        document = Document(uuid4(), "Guide", "guide.txt", "guide.txt", uuid4(), datetime.now(timezone.utc))
        calls: list[str] = []
        documents = InMemoryDocuments(document)
        service = DocumentService(
            documents,
            FakeStorage(calls),
            ingestion=object(),
            vectors=FakeVectors(calls, fail=True),
        )

        with self.assertRaises(DocumentDeletionError):
            service.delete_document(document.id)

        self.assertEqual(calls, ["vectors"])
        self.assertIsNotNone(documents.document)
        self.assertEqual(documents.deleted, [])

    def test_failed_upload_vector_rollback_retains_file_and_record(self) -> None:
        calls: list[str] = []
        documents = InMemoryDocuments(calls=calls)
        service = DocumentService(
            documents,
            FakeStorage(calls),
            ingestion=FailedIngestion(),
            vectors=FakeVectors(calls, fail=True),
        )

        with self.assertRaisesRegex(DocumentUploadError, "vector cleanup could not complete"):
            service.create_document(
                title="Guide",
                filename="guide.txt",
                content=b"guide contents",
                uploaded_by=uuid4(),
                role=UserRole.faculty,
            )

        self.assertEqual(calls, ["metadata-create", "vectors"])
        self.assertIsNotNone(documents.document)
        self.assertEqual(documents.deleted, [])

    def test_ingestion_metadata_retrieval_and_grounded_answer(self) -> None:
        with tempfile.TemporaryDirectory() as path:
            document_id = uuid4()
            file_path = Path(path) / "handbook.txt"
            file_path.write_text("Library hours are Monday through Friday.", encoding="utf-8")
            document = Document(document_id, "Library Handbook", "handbook.txt", str(file_path), uuid4(), datetime.now(timezone.utc))
            documents = InMemoryDocuments(document)
            with isolated_vector_store(Path(path) / "chroma") as vectors:
                ingestion = DocumentIngestionService(
                    documents=documents,
                    extractor=TextExtractionService(),
                    chunker=ChunkingService(chunk_size=80, overlap=5),
                    embeddings=FixedEmbeddings(),
                    vectors=vectors,
                )
                chunk_count = ingestion.ingest_document(document_id)
                retrieval = RetrievalService(FixedEmbeddings(), vectors, top_k=3, max_cosine_distance=1.0)
                llm = CapturingLlm()
                answer = RagService(retrieval, llm).ask("When is the library open?")

        self.assertEqual(chunk_count, 1)
        self.assertEqual(answer["answer"], "Grounded answer")
        self.assertEqual(answer["sources"][0]["document_id"], document_id)
        self.assertEqual(answer["sources"][0]["title"], "Library Handbook")
        self.assertIn("Library hours are Monday through Friday.", llm.calls[0][1])

    def test_no_retrieval_context_returns_controlled_answer_without_llm_call(self) -> None:
        class EmptyRetrieval:
            def retrieve(self, _question: str) -> list[dict[str, object]]:
                return []

        llm = CapturingLlm()
        answer = RagService(EmptyRetrieval(), llm).ask("An unrelated question")

        self.assertEqual(answer, {"answer": NO_CONTEXT_ANSWER, "sources": []})
        self.assertEqual(llm.calls, [])


if __name__ == "__main__":
    unittest.main()
