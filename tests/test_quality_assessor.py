"""Tests for LLM-based document quality assessment, with the Anthropic
client mocked at the SDK boundary -- no real API calls."""

import json

from src.config import settings
from src.pipeline.quality_assessor import assess_quality


class TestAssessQualityWithoutApiKey:
    def test_returns_neutral_defaults_when_no_key_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "")
        result = assess_quality("some document text")

        assert result.readability == 0.5
        assert result.completeness == 0.5
        assert result.structure == 0.5
        assert result.overall == 0.5
        assert result.issues == []


class TestAssessQualityWithMockedClient:
    def test_parses_a_valid_quality_response(self, anthropic_api_key, mock_anthropic):
        mock_anthropic(
            "src.pipeline.quality_assessor",
            json.dumps(
                {
                    "readability": 0.9,
                    "completeness": 0.85,
                    "structure": 0.8,
                    "overall": 0.85,
                    "issues": ["Minor formatting inconsistency on page 3"],
                }
            ),
            input_tokens=90,
            output_tokens=60,
        )

        result = assess_quality("well-structured document text")

        assert result.readability == 0.9
        assert result.completeness == 0.85
        assert result.structure == 0.8
        assert result.overall == 0.85
        assert result.issues == ["Minor formatting inconsistency on page 3"]
        assert result.tokens_used == 150

    def test_parses_response_wrapped_in_markdown_code_fence(
        self, anthropic_api_key, mock_anthropic
    ):
        payload = {
            "readability": 0.4,
            "completeness": 0.3,
            "structure": 0.2,
            "overall": 0.3,
            "issues": ["Document appears truncated", "Poor OCR quality"],
        }
        mock_anthropic("src.pipeline.quality_assessor", f"```json\n{json.dumps(payload)}\n```")

        result = assess_quality("fragmentary scanned text...")
        assert result.overall == 0.3
        assert len(result.issues) == 2

    def test_falls_back_to_zero_defaults_on_malformed_response(
        self, anthropic_api_key, mock_anthropic
    ):
        mock_anthropic("src.pipeline.quality_assessor", "not json at all")

        result = assess_quality("text")

        assert result.readability == 0.0
        assert result.completeness == 0.0
        assert result.structure == 0.0
        assert result.overall == 0.0
