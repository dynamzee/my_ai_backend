from pydantic import BaseModel

class SemanticSearchRequest(BaseModel):
    query: str
    candidates: list[str]

class SemanticSearchMatch(BaseModel):
    text: str
    similarity: float

class SemanticSearchResponse(BaseModel):
    query: str
    best_match: SemanticSearchMatch
    all_matches: list[SemanticSearchMatch] # Ranking in the order of similarity, not just the most similar.

    