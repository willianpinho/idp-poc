"""Embedding generation using Voyage AI or a hash-based fallback."""

import hashlib
import logging
import struct

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text.

    Uses Voyage AI if configured, otherwise falls back to hash-based embeddings.
    """
    if settings.voyage_api_key:
        try:
            return _voyage_embedding(text)
        except Exception as e:
            logger.warning(f"Voyage AI embedding failed, using fallback: {e}")
            return _fallback_embedding(text)

    return _fallback_embedding(text)


def _voyage_embedding(text: str) -> list[float]:
    """Generate embedding using Voyage AI API."""
    truncated = text[:8000]

    response = httpx.post(
        "https://api.voyageai.com/v1/embeddings",
        headers={
            "Authorization": f"Bearer {settings.voyage_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "input": [truncated],
            "model": settings.embedding_model,
        },
        timeout=30.0,
    )
    response.raise_for_status()
    data = response.json()
    embedding = data["data"][0]["embedding"]

    logger.debug(f"Voyage AI embedding generated: {len(embedding)} dimensions")
    return embedding


def _fallback_embedding(text: str, dimensions: int | None = None) -> list[float]:
    """Generate a deterministic hash-based embedding for testing.

    Creates consistent embeddings from text using SHA-256 hashing.
    Identical texts get identical vectors, but no semantic similarity.
    """
    dims = dimensions or settings.embedding_dimensions

    embedding = []
    for i in range(0, dims, 8):
        chunk_hash = hashlib.sha256(f"{text}:{i}".encode()).digest()
        values = struct.unpack("8f", chunk_hash)
        embedding.extend(values)

    # Normalize to unit vector
    embedding = embedding[:dims]
    magnitude = sum(x * x for x in embedding) ** 0.5
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]

    return embedding


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    return [generate_embedding(text) for text in texts]
