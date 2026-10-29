from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChunkRecord(BaseModel):
    id: int
    created_at: datetime

class IngestResponse(BaseModel):
    chunks_created: int
    chunks: list[ChunkRecord]

class AskRequest(BaseModel):
    question : str
    limit: int = 5
    source_document: Optional[str] = None

class SourceReference(BaseModel):
    source_document: Optional[str] = None
    chunk_index: Optional[int] = None
    preview: str

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceReference]

