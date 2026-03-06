"""Vector similarity search for RAG retrieval."""

import logging
from dataclasses import dataclass, field

from src.pipeline.embedder import generate_embedding
from src.storage import database as db

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    page_numbers: list[int] = field(default_factory=list)
    relevance_score: float = 0.0


async def search_similar_chunks(
    document_id: str,
    query: str,
    top_k: int = 5,
) -> list[RetrievedChunk]:
    """Search for document chunks most similar to the query.

    Uses pgvector's cosine distance operator for similarity search.

    Args:
        document_id: UUID of the document to search within.
        query: Natural language query.
        top_k: Number of top results to return.

    Returns:
        List of RetrievedChunk sorted by relevance (most relevant first).
    """
    # Generate query embedding
    query_embedding = generate_embedding(query)
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    # Search using pgvector cosine distance
    rows = await db.fetch(
        """SELECT id, content, page_numbers,
                  1 - (embedding <=> $1::vector) AS relevance_score
           FROM document_chunks
           WHERE document_id = $2
           ORDER BY embedding <=> $1::vector
           LIMIT $3""",
        embedding_str,
        document_id,
        top_k,
    )

    results = []
    for row in rows:
        results.append(RetrievedChunk(
            chunk_id=str(row["id"]),
            content=row["content"],
            page_numbers=row["page_numbers"] or [],
            relevance_score=round(float(row["relevance_score"]), 4),
        ))

    logger.info(
        f"Retrieved {len(results)} chunks for query "
        f"(top score: {results[0].relevance_score if results else 0})"
    )
    return results
