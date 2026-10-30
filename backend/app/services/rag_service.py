"""Coordinate retrieval and grounded answer generation."""

from uuid import UUID

from app.services.llm_service import LLMService, llm_service
from app.services.retrieval_service import RetrievalService, retrieval_service

NO_CONTEXT_ANSWER = (
    "I couldn't find enough information in the knowledge base to answer this question."
)


class RagService:
    def __init__(
        self,
        retrieval: RetrievalService = retrieval_service,
        llm: LLMService = llm_service,
    ) -> None:
        self.retrieval = retrieval
        self.llm = llm

    def ask(self, question: str) -> dict[str, object]:
        chunks = self.retrieval.retrieve(question)
        if not chunks:
            return {"answer": NO_CONTEXT_ANSWER, "sources": []}

        context_parts: list[str] = []
        sources: list[dict[str, object]] = []
        for index, chunk in enumerate(chunks, start=1):
            metadata = chunk["metadata"]
            assert isinstance(metadata, dict)
            text = str(chunk["text"]).strip()
            if not text:
                continue
            context_parts.append(f"[Source {index}]\n{text}")
            try:
                document_id = UUID(str(metadata["document_id"]))
            except (KeyError, TypeError, ValueError):
                continue
            sources.append(
                {
                    "document_id": document_id,
                    "title": str(metadata.get("title") or ""),
                    "filename": str(metadata.get("filename") or ""),
                    "score": float(chunk["score"]),
                }
            )

        if not context_parts:
            return {"answer": NO_CONTEXT_ANSWER, "sources": []}

        context = "\n\n".join(context_parts)
        return {
            "answer": self.llm.generate_answer(question=question, context=context),
            "sources": sources,
        }


rag_service = RagService()
