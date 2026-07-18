from fastapi import APIRouter
from pydantic import BaseModel
from services.claude_ai import generate_claude_ai_response

router = APIRouter()

class ClaudeAIRequest(BaseModel):
    message: str
    system_prompt: str = None

class ClaudeAIResponse(BaseModel):
    response: str
    model: str = "claude-sonnet-4-6"

@router.post("/claude_ai/chat", response_model=ClaudeAIResponse)
async def chat_with_claude(request: ClaudeAIRequest):
    response = await generate_claude_ai_response(
        user_message=request.message,
        system_prompt=request.system_prompt
    )
    return ClaudeAIResponse(response=response)


