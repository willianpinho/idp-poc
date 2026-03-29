"""Text chunking for embedding generation and RAG retrieval."""

import logging
from dataclasses import dataclass, field

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    index: int
    content: str
    page_numbers: list[int] = field(default_factory=list)
    token_count: int = 0


def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~1 token per 4 characters."""
    return len(text) // 4


def chunk_text(
    pages: list[str],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[TextChunk]:
    """Split document text into overlapping chunks for embedding.

    Uses a sliding window approach with configurable chunk size and overlap.
    Tracks which pages each chunk originated from.

    Args:
        pages: List of text strings, one per page.
        chunk_size: Target chunk size in tokens. Defaults to settings.chunk_size.
        chunk_overlap: Overlap between chunks in tokens. Defaults to settings.chunk_overlap.

    Returns:
        List of TextChunk objects.
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    # Convert token sizes to approximate character sizes
    char_size = chunk_size * 4
    char_overlap = chunk_overlap * 4

    # Build a combined text with page boundary markers
    page_boundaries: list[tuple[int, int, int]] = []  # (start_char, end_char, page_num)
    combined = ""
    for page_num, page_text in enumerate(pages):
        start = len(combined)
        combined += page_text + "\n\n"
        end = len(combined)
        page_boundaries.append((start, end, page_num))

    if not combined.strip():
        return []

    chunks: list[TextChunk] = []
    start = 0
    chunk_idx = 0

    while start < len(combined):
        end = min(start + char_size, len(combined))

        # Try to break at sentence boundary
        if end < len(combined):
            # Look for a sentence break near the end
            for sep in [". ", ".\n", "\n\n", "\n", " "]:
                break_pos = combined.rfind(sep, start + char_size // 2, end)
                if break_pos > start:
                    end = break_pos + len(sep)
                    break

        chunk_text_content = combined[start:end].strip()
        if not chunk_text_content:
            break

        # Determine which pages this chunk spans
        chunk_pages = []
        for pb_start, pb_end, page_num in page_boundaries:
            if pb_start < end and pb_end > start:
                chunk_pages.append(page_num)

        chunks.append(
            TextChunk(
                index=chunk_idx,
                content=chunk_text_content,
                page_numbers=chunk_pages,
                token_count=estimate_tokens(chunk_text_content),
            )
        )

        chunk_idx += 1
        # Move forward; if this was the last chunk (end reached combined length), stop
        if end >= len(combined):
            break
        start = max(end - char_overlap, start + 1)  # Always move forward

    logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")
    return chunks
