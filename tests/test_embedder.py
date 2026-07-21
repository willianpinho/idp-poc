"""Tests for embedding generation: the deterministic fallback and the
Voyage AI HTTP call, mocked at the httpx boundary (never live network)."""

import math
from unittest.mock import MagicMock

import pytest

from src.config import settings
from src.pipeline.embedder import (
    _fallback_embedding,
    generate_embedding,
    generate_embeddings_batch,
)


def vectors_equal(a: list[float], b: list[float]) -> bool:
    """Elementwise equality that treats NaN == NaN as equal.

    struct.unpack("8f", ...) reinterprets arbitrary SHA-256 bytes as IEEE-754
    floats, which can legitimately produce NaN components. Python's `==`
    always reports NaN != NaN, so a plain list comparison falsely reports two
    identical, deterministically-derived vectors as unequal.
    """
    return len(a) == len(b) and all(
        (math.isnan(x) and math.isnan(y)) or x == y for x, y in zip(a, b)
    )


class TestFallbackEmbedding:
    def test_is_deterministic_for_the_same_text(self):
        first = _fallback_embedding("hello world")
        second = _fallback_embedding("hello world")
        assert vectors_equal(first, second)

    def test_differs_for_different_text(self):
        assert _fallback_embedding("hello") != _fallback_embedding("goodbye")

    def test_respects_requested_dimensions(self):
        embedding = _fallback_embedding("some text", dimensions=16)
        assert len(embedding) == 16

    def test_produces_a_unit_vector(self):
        embedding = _fallback_embedding("normalize me", dimensions=32)
        magnitude = sum(x * x for x in embedding) ** 0.5
        assert magnitude == pytest.approx(1.0, abs=1e-6)


class TestGenerateEmbeddingDispatch:
    def test_uses_fallback_when_no_voyage_key_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "voyage_api_key", "")
        result = generate_embedding("no key configured")
        assert vectors_equal(result, _fallback_embedding("no key configured"))

    def test_calls_voyage_api_when_key_is_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "voyage_api_key", "test-voyage-key")

        fake_response = MagicMock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}

        fake_post = MagicMock(return_value=fake_response)
        monkeypatch.setattr("src.pipeline.embedder.httpx.post", fake_post)

        result = generate_embedding("call voyage")

        assert result == [0.1, 0.2, 0.3]
        fake_post.assert_called_once()

    def test_falls_back_when_voyage_api_call_raises(self, monkeypatch):
        monkeypatch.setattr(settings, "voyage_api_key", "test-voyage-key")
        monkeypatch.setattr(
            "src.pipeline.embedder.httpx.post",
            MagicMock(side_effect=ConnectionError("network down")),
        )

        result = generate_embedding("voyage is down")
        assert vectors_equal(result, _fallback_embedding("voyage is down"))


class TestGenerateEmbeddingsBatch:
    def test_generates_one_embedding_per_text(self, monkeypatch):
        monkeypatch.setattr(settings, "voyage_api_key", "")
        results = generate_embeddings_batch(["first", "second", "third"])

        assert len(results) == 3
        assert vectors_equal(results[0], _fallback_embedding("first"))
        assert vectors_equal(results[1], _fallback_embedding("second"))
        assert vectors_equal(results[2], _fallback_embedding("third"))
