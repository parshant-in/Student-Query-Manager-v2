"""Retrieve relevant document chunks for a student question."""

from app.core.config import settings
from app.services.embedding_service import EmbeddingService, embedding_service
from app.services.vector_store import VectorStore, vector_store


class RetrievalService:
    def __init__(
        self,
        embeddings: EmbeddingService = embedding_service,
        vectors: VectorStore = vector_store,
        *,
        top_k: int | None = None,
        max_cosine_distance: float | None = None,
    ) -> None:
        self.embeddings = embeddings
        self.vectors = vectors
        self.top_k = settings.RAG_TOP_K if top_k is None else top_k
        self.max_cosine_distance = (
            settings.RAG_MAX_COSINE_DISTANCE
            if max_cosine_distance is None
            else max_cosine_distance
        )

    def retrieve(self, question: str) -> list[dict[str, object]]:
        query_embedding = self.embeddings.embed_query(question)
        matches = self.vectors.search_similar(query_embedding, limit=self.top_k)
        relevant: list[dict[str, object]] = []
        for match in matches:
            distance = match.get("distance")
            if not isinstance(distance, (int, float)) or distance > self.max_cosine_distance:
                continue
            metadata = match.get("metadata")
            relevant.append(
                {
                    "text": str(match.get("text") or ""),
                    "metadata": metadata if isinstance(metadata, dict) else {},
                    # Chroma's cosine distance is smaller for better matches.
                    "score": float(distance),
                }
            )
        return relevant


retrieval_service = RetrievalService()
