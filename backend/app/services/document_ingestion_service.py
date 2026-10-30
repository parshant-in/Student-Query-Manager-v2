"""Connect stored document metadata/files to the RAG ingestion pipeline."""

from pathlib import Path
from uuid import UUID

from app.repositories.document_repository import DocumentRepository
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService, embedding_service
from app.services.text_extraction_service import TextExtractionService
from app.services.vector_store import VectorStore, vector_store


class DocumentIngestionError(Exception):
    pass


class DocumentIngestionService:
    def __init__(
        self,
        documents: DocumentRepository,
        extractor: TextExtractionService,
        chunker: ChunkingService,
        embeddings: EmbeddingService,
        vectors: VectorStore,
    ) -> None:
        self.documents = documents
        self.extractor = extractor
        self.chunker = chunker
        self.embeddings = embeddings
        self.vectors = vectors

    def ingest_document(self, document_id: UUID) -> int:
        try:
            document = self.documents.get_by_id(document_id)
            if document is None:
                raise DocumentIngestionError("Document metadata was not found")

            path = Path(document.file_path)
            if not path.is_absolute():
                backend_root = Path(__file__).resolve().parents[2]
                if not path.is_file() and (backend_root / path).is_file():
                    path = backend_root / path

            text = self.extractor.extract_text(path)
            chunks = self.chunker.chunk_text(text)
            if not chunks:
                raise DocumentIngestionError("Document contains no extractable text")

            embeddings = self.embeddings.embed_chunks(chunks)
            if len(embeddings) != len(chunks):
                raise DocumentIngestionError("Could not create an embedding for every chunk")

            # Replace earlier chunks only after extraction and embedding have succeeded.
            self.vectors.delete_document(document.id)
            self.vectors.add_document_chunks(
                document_id=document.id,
                chunks=chunks,
                embeddings=embeddings,
                filename=document.filename,
                title=document.title,
            )
            return len(chunks)
        except DocumentIngestionError:
            raise
        except Exception as exc:
            raise DocumentIngestionError(
                "Could not extract, embed, or store document chunks."
            ) from exc


document_ingestion_service = DocumentIngestionService(
    documents=DocumentRepository(),
    extractor=TextExtractionService(),
    chunker=ChunkingService(),
    embeddings=embedding_service,
    vectors=vector_store,
)
