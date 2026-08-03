import openai
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel
from config_settings import settings

router = APIRouter(prefix="/openai_one_off", tags=["OPENAI_ONE_OFF."])

client = openai.OpenAI(api_key=settings.openai_api_key)

class OpenAIRequest(BaseModel):
    """
    Exact same shape as claude_one_off.py file.
    The closer the request/response shape are across providers,
    the easier it is to build the agnostic layer on top.
    """
    message: str
    system: str = "You're a helpful assistant."

class OpenAIResponse(BaseModel):
    reply: str
    model: str #OpenAI returns the actual model that responded (useful for logging).
    input_tokens: int
    output_tokens: int

@router.post("/chat", response_model=OpenAIResponse)
async def chat_with_openai(request: OpenAIRequest):
    """
    POST /openai_one_off/chat

    One-off chat with GPT-4o-mini. No memory, no history.
    Equivalent of POST /claude_one_off/chat — same concept, different SDK.

    KEY DIFFERENCES FROM ANTHROPIC:
    1. System prompt goes INSIDE messages as the first item — not a separate param.
    2. Response is at response.choices[0].message.content, not response.content[0].text.
    3. Token field names: prompt_tokens / completion_tokens (not input_tokens / output_tokens).
    """
    logger.info(f"OPENAI_ONE_OFF/CHAT | MESSAGE: {request.message[:60]}")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": request.system}, #system is not a PARAMETER on it's own and NOT optional unlike for anthropic.
                {"role": "user", "content": request.message}
            ]
        )

    except openai.APIStatusError as error:
        logger.error(f"OPENAI API ERROR: {error.status_code}: {error.message}")
        raise HTTPException(status_code=502, detail=f"OpenAI call failed: {error.message}.")
    except openai.APIConnectionError as error:
        logger.error(f"COULDN'T CONNECT TO OPENAI! {error}")
        raise HTTPException(status_code=503, detail="COULDN'T CONNECT TO OPENAI!")

    return OpenAIResponse(
        reply=response.choices[0].message.content,
        model="gpt-4o-mini",
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens
    )





















