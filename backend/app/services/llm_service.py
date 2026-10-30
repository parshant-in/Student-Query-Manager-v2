"""Isolated Gemini provider integration for grounded answer generation."""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = (
    "You are the Student Query Manager knowledge-base assistant. "
    "Answer using only the supplied context. Do not use outside knowledge. "
    "Do not invent policies, dates, rules, fees, faculty information, or other university information. "
    "If the context does not contain enough information, say that the information "
    "is not available in the knowledge base."
)


class LLMConfigurationError(Exception):
    """The provider is not configured for use."""


class LLMProviderError(Exception):
    """The provider could not generate a response."""


class LLMService:
    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = settings.GEMINI_API_KEY if api_key is None else api_key
        self.model = settings.GEMINI_MODEL if model is None else model

    def generate_answer(self, *, question: str, context: str) -> str:
        if not self.api_key.strip():
            raise LLMConfigurationError("Gemini API key is not configured")

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=f"CONTEXT:\n{context}\n\nQUESTION:\n{question}",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS,
                ),
            )
            answer = response.text
        except Exception as exc:
         logger.exception("Gemini provider failed while answering a question: %s", exc)
         raise LLMProviderError("The answer service could not generate a response")

        if not answer or not answer.strip():
            raise LLMProviderError("Gemini returned an empty answer")
        return answer.strip()


llm_service = LLMService()
