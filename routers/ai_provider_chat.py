from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel
from typing import Literal
from services.ai_provider import chat_with_ai_provider

router = APIRouter(prefix="/ai", tags=["AI - PROVIDER_AGNOSTIC."])

class AIProviderChatRequest(BaseModel):
    """
    Literal["anthropic", "openai"] — Stating the options is literally anthropic and openai.
    """
    message: str
    provider: Literal["anthropic", "openai"] = "anthropic"
    system: str = "You're a helpful assistant."

class AIProviderChatResponse(BaseModel):
    reply: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int

@router.post("/chat", response_model=AIProviderChatResponse)
async def chat_with_provider_agnostic_ai(request: AIProviderChatRequest):
    """
    POST /ai/chat

    One endpoint. Two providers. Client picks which one via the 'provider' field.
    """
    try:
        ai_response = chat_with_ai_provider(
            message=request.message,
            provider=request.provider,
            system=request.system
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        logger.error(f"PROVIDER CHAT ERROR [{request.provider}]: {error}")
        raise HTTPException(status_code=502, detail="An unexpected error occurred.")

    return AIProviderChatResponse(**ai_response)




















