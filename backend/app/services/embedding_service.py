"""Local CPU embeddings using a lazily loaded Sentence Transformers model."""

from typing import Any

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name, device="cpu")
        return self._model

    def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        if not chunks:
            return []
        vectors: Any = self._get_model().encode(
            chunks, convert_to_numpy=True, show_progress_bar=False
        )
        return vectors.tolist()

    def embed_query(self, query: str) -> list[float]:
        vector: Any = self._get_model().encode(
            query, convert_to_numpy=True, show_progress_bar=False
        )
        return vector.tolist()


embedding_service = EmbeddingService()
