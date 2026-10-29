"""
RAG -- RETRIEVAL AUGMENTED GENERATION.

Every piece already exists in this project, Today wires them together.

RETRIEVAL: search_similar_chunks() from day 20 finds the chunk whose meaning is closest to the question.

AUGMENTED: those chunks get inserted directly into the prompt sent to Claude-- thereby "augmenting" what
Claude would otherwise only know from its own training.

GENERATION: Claude writes the answer, grounded in that context instead of guessing from general knowledge.

THE GENUINELY NEW PIECE: Instructing Claude to answer ONLY from the provided context, and say so plainly
when it CAN'T. Without this rule, Claude might quietly fall back on its own training knowledge-- which
defeats the entire point of grounding answers in YOUR documents.
"""
import anthropic
from loguru import logger
from config_settings import settings
from services.vector_store_search import search_similar_chunks

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

RAG_SYSTEM_PROMPT = """You're a helpful assistant answering questions using only the context provided below.

<context>
{context}
</context>

CRITICAL RULES:
1. Answer using ONLY information found in the context above.
2. If the context does not contain enough information to answer, say so plainly. Do not guess, and do not use outside knowledge.
3. Keep every claim traceable to something actually written in the context.
"""

async def answer_from_provided_documents(question: str, limit: int = 5, source_document: str | None = None) -> dict:
    """The full loop: embed the question, retrieve chunks, hand them to Claude, return a grounded answer."""
    logger.info(f"RAG query | question: '{question[:60]}'")

    retrieved = await search_similar_chunks(question, limit, source_document)

    if not retrieved:
        if source_document:
            message = f"No stored chunks found for '{source_document}'. Check the name and try again."
        else:
            message = "No documents have been stored yet."
        return {"answer": message, "sources": []}

    context_block = "\n\n ******************* \n\n".join(chunk["text"] for chunk in retrieved)

    try:
        response = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=1024,
            system=RAG_SYSTEM_PROMPT.format(context=context_block),
            messages=[{"role": "user", "content": question}]
        )
    except anthropic.APIStatusError as error:
        logger.error(f"{type(error).__name__} {error.status_code} | {error.message} | request_id={error.request_id}")
        if error.status_code == 429 or error.status_code >= 500:
            raise ValueError("The AI service is busy right now. Please try again shortly.")
        raise ValueError("The AI service rejected this request.")
    except anthropic.APIConnectionError as error:
        logger.error(f"{type(error).__name__} | {error} | cause: {error.__cause__!r}")
        raise ValueError("Couldn't reach the AI service. Please try again.")

    return {
        "answer": response.content[0].text,
        "sources": [{"source_document": source["source_document"], "chunk_index": source["chunk_index"],
                     "preview": source["text"][:100]} for source in retrieved]
    }


