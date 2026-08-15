from pydantic import BaseModel, Field
from typing import Literal, Optional

class ExtractedTask(BaseModel):
    """
    The exact shape that Claude's output will be forced into.

    Same pydantic pattern I've used for every client request so far;
    the difference is that now-- it validates the AI (Claude) OUTPUT instead of the CLIENT'S INPUT.

    Same principle applies: To not trust text that you didn't generate by yourself.
    The AI's input is untrusted input, exactly like a request body.
    """
    title: str
    priority: Literal["low", "medium", "high"]
    category: str
    due_date: Optional[str] = Field(
        default=None,
        description="YYYY-MM-DD if a date is mentioned in the text, otherwise null."
    )

class TaskExtractionRequest(BaseModel):
    text: str

class TaskPipelineResponse(BaseModel):
    task: ExtractedTask
    notification: str



