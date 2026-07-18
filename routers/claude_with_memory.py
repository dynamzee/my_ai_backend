import os
import anthropic
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import APIRouter, HTTPException
from loguru import logger

class Settings(BaseSettings):
    anthropic_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()

from schemas.claude import ClaudeRequest, ClaudeResponse, ClaudeMessage

router = APIRouter(prefix="/claude_with_memory", tags=["Claude chat --> Multi-turn."])

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

@router.post("/claude", response_model=ClaudeResponse)
async def multi_turn_chat(claude: ClaudeRequest):
    """
    POST /claude_with_memory/claude

    Multi-turn conversation with Claude.

     Claude is stateless --> every API call is a fresh HTTP request to anthropic.
     It has no memory of previous calls. We solve this by sending the ENTIRE
     conversation history on every single request. Claude reads it from top
     to bottom and responds with full context.

     The client (user) is responsible for:
     1. Storing the 'messages' list from our response.
     2. Sending it back to us on the next request.

     We (assistant) are responsible for:
     1. Appending the new user message to the history.
     2. Calling Claude with the full conversation history.
     3. Appending Claude's response to the history.
     4. Returning the updated history to the client.
    """

    claude_api_messages = [
        {"role": message.role, "content": message.content}
        for message in claude.messages
    ]

    claude_api_messages.append({"role": "user", "content": claude.user_message})
    logger.info(
        f"Multi-turn chat | existing turns: {len(claude.messages) // 2}"
        f"| new message: '{claude.user_message[:60]}'"
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=claude_api_messages
        )
    except anthropic.APIStatusError as error:
        logger.error(f"ANTHROPIC API ERROR: {error.status_code}: {error.message}")
        raise HTTPException(status_code=502, detail=f"CLAUDE AI CALL FAILED: {error.message}")
    except anthropic.APIConnectionError as error:
        logger.error(f"ANTHROPIC CONNECTION ERROR: {error}")
        raise HTTPException(status_code=503, detail="COULD NOT REACH ANTHROPIC.")

    claude_response = response.content[0].text

    entire_conversation = claude.messages + [
        ClaudeMessage(role="user", content=claude.user_message),
        ClaudeMessage(role="assistant", content=claude_response)
    ]
    logger.info(
        f"Multi_chat turn complete | total turns now: {len(entire_conversation) // 2}"
        f"| tokens used: input_tokens={response.usage.input_tokens} || output_tokens={response.usage.output_tokens}"
    )

    return ClaudeResponse(
        reply=claude_response,
        messages=entire_conversation,
        turn_count=len(entire_conversation) // 2
    )



