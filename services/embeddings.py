"""
EMBEDDINGS + SEMANTIC SEARCH.

CORE FACT: Claude generates text. It does not, and Anthropic does not
offer any product that does embeddings: which is converting text into
a vector. Embeddings are genuinely a different kind of model, not lesser
than Claude in the sense that it does not generate text. It does something
entirely different.
Anthropic own docs confirm this and point developers to third-party providers.
Since OpenAI offers embedding and I have already built a provider-agnostic layer
covering both ANTHROPIC & OPENAI (shows the importance of the agnostic layer, it
wasn't just an ANTHROPIC vs OPENAI thing. My project has been dominated by Anthropic,
but here I'm switching to OpenAI for an infrastructure that my project needs but Anthropic
doesn't offer); I'll use OpenAI's text-embedding-3-small here which returns 1536-dimensional vectors.
"""

import math
import openai
from loguru import logger
from config_settings import settings

client = openai.OpenAI(api_key=settings.openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"

def get_embedding(text: str) -> list[float]:
    """
    Converts ONE piece of text into a 1536-number vector representing its meaning.
    Same text always produces the same vector-- no room for randomness, unlike when
    compared to a normal call to Claude.
    """
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding

def get_embedding_in_batch(texts: list[str]) -> list[list[float]]:
    """
    Embeds multiple text in one API call instead of looping get_embedding()
    x times. OpenAI's endpoint accepts a list directly, and response.data comes
    back in the same order you sent the text in-- results[i] always matches texts[i].
    One network round trip instead of x times.
    """
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [embedded_lists.embedding for embedded_lists in response.data]

def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """
    Measures how aligned two (2) vectors DIRECTIONS are, ignoring their length.
    It's roughly -1 to 1. Closer to 1 = closer in meaning. Real text embeddings
    in practice usually land somewhere between 0 and 1.
    """
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))
    return dot_product / (magnitude_a * magnitude_b)

def semantic_search(query: str, candidates: list[str]) -> list[dict]:
    """
    Ranks every candidate by CLOSENESS in MEANING to the query -- not by shared
    words. Embeds the query once, embeds all candidates in a single batched call.
    Scores each with cosine similarity and sorts best-first.
    """
    logger.info(f"SEMANTIC SEARCH| QUERY: '{query[:60]}'| CANDIDATES: {len(candidates)}")

    query_vector = get_embedding(query)
    candidates_vector = get_embedding_in_batch(candidates)

    results = [
        {"text": text, "similarity": cosine_similarity(query_vector, candidate_vector)}
        for text, candidate_vector in zip(candidates, candidates_vector)
    ]

    results.sort(key=lambda response: response["similarity"], reverse=True)
    return results






