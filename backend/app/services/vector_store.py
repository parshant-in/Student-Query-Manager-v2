"""Persistent local ChromaDB storage for document chunks and embeddings."""

from pathlib import Path
from uuid import UUID

import chromadb


class VectorStore:
    def __init__(self, persist_directory: str | Path | None = None) -> None:
        if persist_directory is None:
            backend_root = Path(__file__).resolve().parents[2]
            persist_directory = backend_root / "storage" / "vector_store"
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self.persist_directory))
        self._collection = self._client.get_or_create_collection(
            name="document_chunks", metadata={"hnsw:space": "cosine"}
        )

    def close(self) -> None:
        """Release the local Chroma client, useful for isolated test stores."""
        self._client._system.stop()

    def add_document_chunks(
        self,
        *,
        document_id: UUID,
        chunks: list[str],
        embeddings: list[list[float]],
        filename: str,
        title: str,
    ) -> list[str]:
        if len(chunks) != len(embeddings):
            raise ValueError("Each chunk must have exactly one embedding")
        if not chunks:
            return []

        document_id_text = str(document_id)
        ids = [f"{document_id_text}:{index}" for index in range(len(chunks))]
        metadatas = [
            {"document_id": document_id_text, "filename": filename, "title": title}
            for _ in chunks
        ]
        self._collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return ids

    def search_similar(
        self,
        query_embedding: list[float],
        *,
        limit: int = 5,
        where: dict[str, str] | None = None,
    ) -> list[dict[str, object]]:
        collection_size = self._collection.count()
        if limit <= 0 or collection_size == 0:
            return []
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(limit, collection_size),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            {
                "id": ids[index],
                "text": documents[index],
                "metadata": metadatas[index],
                "distance": distances[index],
            }
            for index in range(len(ids))
        ]

    def delete_document(self, document_id: UUID) -> None:
        self._collection.delete(where={"document_id": str(document_id)})


vector_store = VectorStore()
