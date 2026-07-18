from pydantic import BaseModel
from typing import Literal

class ClaudeMessage(BaseModel):
    """
    A single turn in a conversation.

    role must be "user" or "assistant" --> Anthropic enforces strict alternation.
    Two user messages in a row = API validation error. Keep this in mind.
    """
    role: Literal["user", "assistant"]
    content: str

class ClaudeRequest(BaseModel):
    """
    What the client sends us on every request.

    messages:     Full conversation history up to this point.
                  empty list = brand-new conversation (perfectly valid)
    user_message: the new thing the user wants to say this point.
    """

    messages: list[ClaudeMessage] = []
    user_message: str

class ClaudeResponse(BaseModel):
    """
    What we send back after Claude responds.

    reply:      Claude's response this turn; easy access without digging.
    messages:   Full updated history including this turn.
                CLIENT MUST STORE THIS AND SEND ON THE NEXT REQUEST.
                THE CLIENT IS THE MEMORY, THIS IS THE WHOLE PATTERN.
    turn_count: one user + assistant exchange = one turn.
    """
    reply: str
    messages: list[ClaudeMessage]
    turn_count: int



