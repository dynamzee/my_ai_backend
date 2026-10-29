"""
VECTOR STORAGE-- persisting embeddings in Postgres via pgvector.

Previously on this project (Embeddings, Vector, Cosine_Similarity and Semantic search.):
semantic_search() recomputed every candidate's embedding on every request, from a list that
only lived in memory for that one request. But for this one: embeddings get COMPUTED once,
stored permanently, and Postgres itself finds the closest matches using its HNSW index-- not
a python for loop checking every row one at a time.
"""

from database_connection import get_pool
from services.embeddings import get_embedding, get_embedding_in_batch

async def store_chunk(text: str) -> dict:
    """Embeds text and stores it permanently. Returns the new row's dict (id and created_at)."""
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

async def store_chunks_batch(texts: list[str], source_document: str) -> list[dict]:
    """
    Embeds and stores MULTIPLE chunks efficiently -- one batched embedding call instead of
    looping get_embedding() x number of times and also -- one borrowed connection reused for
    every INSERT instead of acquiring a fresh one per chunk.
    """
    embeddings = get_embedding_in_batch(texts)
    pool = get_pool()
    records = []

    async with pool.acquire() as connection:
        for index, (text, embedding) in enumerate(zip(texts, embeddings)):
            row = await connection.fetchrow(
                """
                INSERT INTO document_chunks(content, embedding, source_document, chunk_index)
                VALUES ($1, $2::vector, $3, $4)
                RETURNING id, created_at
                """,
                text,
                str(embedding),
                source_document,
                index
            )
            records.append({"id": row["id"], "created_at": row["created_at"]})

    return records

async def search_similar_chunks(query: str, limit: int = 5, source_document: str | None = None) -> list[dict]:
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
            SELECT id, content, source_document, chunk_index, embedding <=> $1::vector AS distance
            FROM document_chunks
            WHERE ($3::text IS NULL OR source_document = $3)
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            str(query_embedding),
            limit,
            source_document
        )
    return [
        {"id": row["id"], "text": row["content"], "source_document": row["source_document"],
         "chunk_index": row["chunk_index"], "similarity": 1 - row["distance"]}
        for row in rows
    ]


