from fastapi import APIRouter, HTTPException
from schemas.embeddings import SemanticSearchRequest, SemanticSearchMatch, SemanticSearchResponse
from services.embeddings import semantic_search
from loguru import logger

router = APIRouter(prefix="/embedding", tags=["EMBEDDINGS | SEMANTIC SEARCH."])

@router.post("/semantic_search", response_model=SemanticSearchResponse)
async def semantic_search_endpoint(request: SemanticSearchRequest):
    """
    POST /embedding/semantic_search

    Given a query and a list of candidates sentences, find the one closest in meaning.
    NOT the one sharing the most literal words.
    """
    if not request.candidates:
        raise HTTPException(status_code=400, detail="Candidates list cannot be empty!")
    try:
        ranked_responses = semantic_search(request.query, request.candidates)
    except Exception as error:
        logger.error(f"SEMANTIC SEARCH FAIL: {error}")
        raise HTTPException(status_code=502, detail="SEMANTIC SEARCH FAILED! PLEASE TRY AGAIN.")

    matched_responses = [SemanticSearchMatch(**response) for response in ranked_responses]

    return SemanticSearchResponse(
        query=request.query,
        best_match=matched_responses[0],
        all_matches=matched_responses
    )

