"""Request and response schemas for grounded knowledge-base questions."""

from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RagAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def strip_nonempty_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question must not be blank")
        return value


class RagSource(BaseModel):
    document_id: UUID
    title: str
    filename: str
    score: float = Field(description="Chroma cosine distance; lower values are closer matches")


class RagAskResponse(BaseModel):
    answer: str
    sources: list[RagSource]
