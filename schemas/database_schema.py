from pydantic import BaseModel
from datetime import datetime

class StoreChunkRequest(BaseModel):
    text: str

class StoreChunkResponse(BaseModel):
    id: int
    text: str
    created_at: datetime

class VectorSearchRequest(BaseModel):
    query: str
    limit: int = 5

class VectorSearchMatch(BaseModel):
    id: int
    text: str
    similarity: float

class VectorSearchResponse(BaseModel):
    query: str
    matches: list[VectorSearchMatch]


