"""Tests for LLM-based metadata extraction, with the Anthropic client mocked
at the SDK boundary -- no real API calls."""

import json

from src.config import settings
from src.pipeline.extractor import extract_metadata


class TestExtractMetadataWithoutApiKey:
    def test_returns_empty_result_when_no_key_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "")
        result = extract_metadata("some document text")

        assert result.title is None
        assert result.key_entities == []
        assert result.key_terms == []
        assert result.average_confidence == 0.0


class TestExtractMetadataWithMockedClient:
    FULL_RESPONSE = {
        "title": {"value": "Software Development Agreement", "confidence": 0.95},
        "author": {"value": "TechVision Solutions Inc.", "confidence": 0.8},
        "date": {"value": "2025-01-15", "confidence": 0.9},
        "language": {"value": "en", "confidence": 0.99},
        "summary": {"value": "A contract for e-commerce platform development.", "confidence": 0.85},
        "key_entities": [
            {"name": "TechVision Solutions Inc.", "type": "organization", "confidence": 0.9},
            {"name": "GlobalRetail Corp.", "type": "organization", "confidence": 0.88},
        ],
        "key_terms": ["software development", "e-commerce", "agreement"],
    }

    def test_parses_all_fields_from_a_full_response(self, anthropic_api_key, mock_anthropic):
        mock_anthropic(
            "src.pipeline.extractor",
            json.dumps(self.FULL_RESPONSE),
            input_tokens=200,
            output_tokens=150,
        )

        result = extract_metadata("Software Development Agreement text...")

        assert result.title == "Software Development Agreement"
        assert result.title_confidence == 0.95
        assert result.author == "TechVision Solutions Inc."
        assert result.document_date == "2025-01-15"
        assert result.language == "en"
        assert result.summary == "A contract for e-commerce platform development."
        assert len(result.key_entities) == 2
        assert result.key_entities[0].name == "TechVision Solutions Inc."
        assert result.key_terms == ["software development", "e-commerce", "agreement"]
        assert result.tokens_used == 350

    def test_average_confidence_ignores_zero_confidence_fields(
        self, anthropic_api_key, mock_anthropic
    ):
        response = {
            "title": {"value": "Doc", "confidence": 1.0},
            "author": {"value": None, "confidence": 0.0},
            "date": {"value": None, "confidence": 0.0},
            "language": {"value": "en", "confidence": 1.0},
            "summary": {"value": "s", "confidence": 0.0},
            "key_entities": [],
            "key_terms": [],
        }
        mock_anthropic("src.pipeline.extractor", json.dumps(response))

        result = extract_metadata("text")
        # Only title and language have non-zero confidence: average = 1.0
        assert result.average_confidence == 1.0

    def test_caps_entities_and_terms_at_ten(self, anthropic_api_key, mock_anthropic):
        response = {
            "title": {"value": None, "confidence": 0.0},
            "author": {"value": None, "confidence": 0.0},
            "date": {"value": None, "confidence": 0.0},
            "language": {"value": None, "confidence": 0.0},
            "summary": {"value": None, "confidence": 0.0},
            "key_entities": [
                {"name": f"Entity {i}", "type": "other", "confidence": 0.5} for i in range(15)
            ],
            "key_terms": [f"term{i}" for i in range(15)],
        }
        mock_anthropic("src.pipeline.extractor", json.dumps(response))

        result = extract_metadata("text")
        assert len(result.key_entities) == 10
        assert len(result.key_terms) == 10

    def test_returns_empty_result_on_malformed_response(self, anthropic_api_key, mock_anthropic):
        mock_anthropic("src.pipeline.extractor", "not json")

        result = extract_metadata("text")
        assert result.title is None
        assert result.key_entities == []
