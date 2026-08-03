import anthropic
from config_settings import settings
from fastapi import HTTPException

async def generate_claude_ai_response(user_message: str, system_prompt: str = None) -> str:
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        parameters = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }

        if system_prompt:
            parameters["system"] = system_prompt

        message = client.messages.create(**parameters)
        return message.content[0].text

    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid Anthropic API_Key.")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit reached. Try again shortly.")
    except anthropic.APIError as error:
        raise HTTPException(status_code=503, detail=f"AI Service Error: {str(error)}")


