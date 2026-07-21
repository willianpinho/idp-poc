"""Tests for LLM-based document classification, with the Anthropic client
mocked at the SDK boundary -- no real API calls."""

import json

from src.config import settings
from src.pipeline.classifier import classify_document


class TestClassifyDocumentWithoutApiKey:
    def test_returns_default_other_category_when_no_key_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "")
        result = classify_document("some document text")

        assert result.category == "other"
        assert result.confidence == 0.0
        assert result.tokens_used == 0


class TestClassifyDocumentWithMockedClient:
    def test_parses_a_valid_classification_response(self, anthropic_api_key, mock_anthropic):
        mock_anthropic(
            "src.pipeline.classifier",
            json.dumps(
                {
                    "category": "invoice",
                    "confidence": 0.92,
                    "reasoning": "Contains line items and a total due",
                }
            ),
            input_tokens=120,
            output_tokens=40,
        )

        result = classify_document("Invoice #123\nTotal: $500")

        assert result.category == "invoice"
        assert result.confidence == 0.92
        assert result.reasoning == "Contains line items and a total due"
        assert result.tokens_used == 160

    def test_parses_response_wrapped_in_markdown_code_fence(
        self, anthropic_api_key, mock_anthropic
    ):
        payload = {"category": "contract", "confidence": 0.8, "reasoning": "Legal agreement"}
        mock_anthropic("src.pipeline.classifier", f"```json\n{json.dumps(payload)}\n```")

        result = classify_document("This agreement is entered into...")
        assert result.category == "contract"
        assert result.confidence == 0.8

    def test_falls_back_to_other_on_malformed_response(self, anthropic_api_key, mock_anthropic):
        mock_anthropic("src.pipeline.classifier", "not valid json at all")

        result = classify_document("ambiguous text")

        assert result.category == "other"
        assert result.confidence == 0.3
        assert "Parse error" in result.reasoning

    def test_defaults_missing_confidence_to_half(self, anthropic_api_key, mock_anthropic):
        mock_anthropic(
            "src.pipeline.classifier",
            json.dumps({"category": "report", "reasoning": "Looks like a report"}),
        )

        result = classify_document("quarterly numbers")
        assert result.confidence == 0.5
