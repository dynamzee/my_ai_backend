from fastapi import APIRouter, HTTPException, UploadFile, File
from loguru import logger
from schemas.rag import ChunkRecord, IngestResponse, AskRequest, AskResponse
from services.chunking import chunk_text
from services.vector_store_search import store_chunks_batch
from services.rag_pipeline import answer_from_provided_documents

router = APIRouter(prefix="/documents", tags=["RAG- Document Ingestion + Q&A."])

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    POST /documents/ingest

    Accepts a text file, chunks it, embeds every chunk, stores all of them.

    file.read() returns raw BYTES - same as every response I've decoded since day 16.
    .decode("utf-8") turns those bytes into a real string before chunking touches it.
    """
    raw_bytes = await file.read()

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be a plain utf-8 file.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="File is empty.")

    chunks = chunk_text(text)
    logger.info(f"CHUNKED '{file.filename}' | {len(chunks)} chunks created.")

    try:
        chunk_records = await store_chunks_batch(chunks, file.filename or "unnamed")
    except Exception:
        logger.exception("INGESTION FAILED")
        raise HTTPException(status_code=502, detail="Ingestion failed. Please try again.")
    logger.info(f"STORED '{file.filename}' | {len(chunk_records)} chunks.")

    return IngestResponse(
        chunks_created=len(chunk_records),
        chunks=[ChunkRecord(**record) for record in chunk_records]
    )

@router.post("/ask", response_model=AskResponse)
async def ask_endpoint(request: AskRequest):
    """
    POST /documents/ask

    The full RAG loop: embed the question, retrieve the closest stored chunks, hand them to Claude
    as grounding, return a traceable answer.
    """
    try:
        result = await answer_from_provided_documents(request.question, request.limit, request.source_document)
    except ValueError as error:
        raise HTTPException(status_code=502, detail=str(error))
    except Exception:
        logger.exception("RAG QUERY FAILED")
        raise HTTPException(status_code=502, detail="QUESTION ANSWERING FAILED. PLEASE TRY AGAIN.")

    return AskResponse(question=request.question, answer=result["answer"], sources=result["sources"])





