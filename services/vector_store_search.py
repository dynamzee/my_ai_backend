"""
VECTOR STORAGE-- persisting embeddings in Postgres via pgvector.

Previously on this project (Embeddings, Vector, Cosine_Similarity and Semantic search.):
semantic_search() recomputed every candidate's embedding on every request, from a list that
only lived in memory for that one request. But for this one: embeddings get COMPUTED once,
stored permanently, and Postgres itself finds the closest matches using its HNSW index-- not
a python for loop checking every row one at a time.
"""

from database_connection import get_pool
from services.embeddings import get_embedding

async def store_chunk(text: str) -> dict:
    """Embeds text and stores it permanently. Returns the new row's ID."""
    embedding = get_embedding(text)
    pool = get_pool()

    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            """
            INSERT INTO document_chunks(content, embedding)
            VALUES ($1, $2::vector)
            RETURNING id, created_at
            """,
            text,
            str(embedding)
        )
    return {"id": row["id"], "created_at": row["created_at"]}

async def search_similar_chunks(query: str, limit: int = 5) -> list[dict]:
    """
    Embeds the query, then asks POSTGRES to find the closest stored chunks-- using <=>,
    which pgvector reads as COSINE DISTANCE (0 = identical | higher than 0 = less related.)
    This is opposite direction from the COSINE SIMILARITY I used previously.
    """
    query_embedding = get_embedding(query)
    pool = get_pool()

    async with pool.acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT ID, content, embedding <=> $1::vector AS distance
            FROM document_chunks
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            str(query_embedding),
            limit
        )
    return [
        {"id": row["id"], "text": row["content"], "similarity": 1 - row["distance"]}
        for row in rows
    ]






























