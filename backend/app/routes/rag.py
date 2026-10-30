"""Authenticated student endpoint for grounded knowledge-base answers."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.schemas.rag import RagAskRequest, RagAskResponse
from app.services.llm_service import LLMConfigurationError, LLMProviderError
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ask", response_model=RagAskResponse)
def ask_question(
    request: RagAskRequest,
    current_user: User = Depends(get_current_user),
) -> RagAskResponse:
    if current_user.role != UserRole.student:
        raise HTTPException(status_code=403, detail="Student role required")
    try:
        return RagAskResponse(**rag_service.ask(request.question))
    except LLMConfigurationError:
        raise HTTPException(
            status_code=503,
            detail="The answer service is not configured",
        ) from None
    except LLMProviderError:
        logger.error("Gemini provider failed while answering a question")
        raise HTTPException(
            status_code=502,
            detail="The answer service could not generate a response",
        ) from None
    except Exception:
        logger.exception("Unexpected error while answering a student question")
        raise HTTPException(
            status_code=500,
            detail="Could not process the question",
        ) from None
