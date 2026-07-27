import anthropic
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel
from config_settings import settings

router = APIRouter(prefix="/claude_streaming", tags=["CLAUDE - STREAMING"])

async_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

class StreamingRequest(BaseModel):
    """
    Simple request for a one-off streaming response.
    Streaming request equivalent of claude_one_off -- no history/memory. Just one message.
    Streaming + memory together comes later.
    """
    message: str
    system: str = "You're a helpful assistant."

async def streaming_token_generator(message: str, system: str):
    """
    Async generator that yields tokens from Claude one by one.

    The moment Anthropic generates a token on their end, it arrives here.
    We yield it immediately. FastAPI's StreamingResponse picks it up and
    pushes it straight to the client — no buffering, no waiting.

    'async with' — async context manager. Opens the streaming connection
    to Anthropic, gives us the stream object, and guarantees the connection
    is properly closed when we're done (even if an error occurs mid-stream).

    'async for text in stream.text_stream' — iterates over tokens as they
    arrive. Each iteration gives us one chunk (sometimes a word, sometimes
    a few characters — Anthropic decides the chunk size).
    """
    try:
        async with async_client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": message}]
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except anthropic.APIStatusError as error:
        logger.error(f"ANTHROPIC API ERROR = {error.status_code}: {error.message}")
        yield f"\n[ERROR: {error.message}]"
    except anthropic.APIConnectionError as error:
        logger.error(f"ANTHROPIC API CONNECTION ERROR: {error}")
        yield "\n[ERROR: COULDN'T CONNECT TO ANTHROPIC API]"

@router.post("/streaming")
async def streaming_response(request: StreamingRequest):
    """
    POST /claude_streaming/streaming

    Streams Claude's response token by token — just like claude.ai.

    StreamingResponse takes our generator and keeps the HTTP connection
    open, forwarding each yielded token to the client the moment it arrives.
    media_type="text/plain" tells the client to expect a continuous stream
    of plain text, not a single JSON blob.

    IMPORTANT — Swagger UI limitation:
    Swagger buffers the entire response before displaying it, so /docs
    will look like a normal slow response. The streaming is still happening
    — Swagger just hides it. Test with curl or the Python script below
    to actually watch tokens arrive one by one.
    """
    logger.info(f"STREAM REQUEST | MESSAGE '{request.message[:60]}'")

    return StreamingResponse(
        streaming_token_generator(request.message, request.system),
        media_type="text/plain"
    )



