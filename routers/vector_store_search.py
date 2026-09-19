from fastapi import APIRouter, HTTPException
from loguru import logger
from schemas.database_schema import StoreChunkRequest, StoreChunkResponse, VectorSearchRequest, VectorSearchResponse, VectorSearchMatch
from services.vector_store_search import store_chunk, search_similar_chunks

router = APIRouter(prefix="/vector_store", tags=["VECTOR DATABASE - PGVECTOR"])

@router.post("/store", response_model=StoreChunkResponse)
async def store_chunk_endpoint(request: StoreChunkRequest):
    """POST /vector_store/store-- Embeds text, stores it permanently in Postgres."""
    try:
        created = await store_chunk(request.text)
    except Exception as error:
        logger.error(f"FAILED TO STORE CHUNK: {error}")
        raise HTTPException(status_code=502, detail="FAILED TO STORE CHUNK, PLEASE TRY AGAIN.")
    return StoreChunkResponse(id=created["id"], text=request.text, created_at=created["created_at"])

@router.post("/search", response_model=VectorSearchResponse)
async def search_similar_chunk_endpoint(request: VectorSearchRequest):
    """POST /vector_store/search-- Find the closest stored chunks via Postgres, not a python loop."""
    try:
        results = await search_similar_chunks(request.query, request.limit)
    except Exception as error:
        logger.error(f"VECTOR SEARCH FAILED: {error}")
        raise HTTPException(status_code=503, detail="VECTOR SEARCH FAILED, PLEASE TRY AGAIN.")
    matches = [VectorSearchMatch(**response) for response in results]
    return VectorSearchResponse(query=request.query, matches=matches)




