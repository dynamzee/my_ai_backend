"""
PROVIDER-AGNOSTIC AI SERVICE LAYER.

The problem this solves?
My endpoints shouldn't care about which LLM they're talking to -- same structure built-in.
A client says "use OpenAI instead of Claude" — I only have to change a config flag,
not my entire codebase. This is what AI integration engineering actually means.

If I decide to add a new provider (Gemini, Mistral, Cohere, Copilot) → I'll just need to install and add the block.
Nothing else in my codebase changes.
"""

import anthropic
import openai
from loguru import logger
from config_settings import settings

anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
openai_client = openai.OpenAI(api_key=settings.openai_api_key)

SUPPORTED_PROVIDERS = ["anthropic", "openai"]

def chat_with_ai_provider(
    message: str,
    provider: str = "anthropic",
    system: str = "You're a helpful assistant.",
) -> dict:
    """
    Just one function. Any supported provider. Same return shape every time.

    The router calls this. The router doesn't touch any SDK directly.
    If Anthropic changes their SDK tomorrow, I'll fix it here - same place.
    """

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"{provider} is not supported currently. Our supported providers: {SUPPORTED_PROVIDERS}")

    logger.info(f"PROVIDER-AGNOSTIC AI PROVIDER| PROVIDER = {provider}| USER_MESSAGE: {message[:60]}")

    if provider == "anthropic":
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": message}]
            )
            return {
                "reply": response.content[0].text,
                "provider": "anthropic",
                "model": response.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens

            }

    elif provider == "openai":
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message}
            ]
        )
        return {
            "reply": response.choices[0].message.content,
            "provider": "openai",
            "model": response.model,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens
        }




