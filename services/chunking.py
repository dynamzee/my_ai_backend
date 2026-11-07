"""
DOCUMENT CHUNKING.

A single embedding can't usefully represent fifty (50) pages-- everything it discusses gets
averaged into one (1) point, too diluted to distinguish one topic from another. CHUNKING breaks
a document into smaller pieces, each small enough to actually be ABOUT something specific.
"""

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split texts into overlapping chunks of roughly "chunk_size" characters.

    OVERLAP exists because a hard cut can slice a sentence -- or an idea -- right down the middle.
    Without overlap, chunk 1 might end mid-thought, and chunk 2 opens with zero context for finishing
    it. A 200-character overlap means the tail of one chunk reappears at the start of the next, so a boundary
    rarely destroys meaning completely.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size, or chunking never advances.")

    chunks = []
    chunks_start = 0
    while chunks_start < len(text):
        chunks_end = chunks_start + chunk_size
        chunk = text[chunks_start:chunks_end].strip()
        if chunk:
            chunks.append(chunk)
        chunks_start += chunk_size - overlap

    return chunks





