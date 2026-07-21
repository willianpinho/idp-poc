"""Tests for LLM response parsing helpers."""

import json

import pytest

from src.pipeline.llm_utils import parse_json_response


class TestParseJsonResponse:
    def test_parses_plain_json(self):
        raw = json.dumps({"category": "invoice", "confidence": 0.9})
        assert parse_json_response(raw) == {"category": "invoice", "confidence": 0.9}

    def test_parses_json_wrapped_in_json_labeled_code_fence(self):
        payload = {"category": "contract", "confidence": 0.8}
        raw = f"```json\n{json.dumps(payload)}\n```"
        assert parse_json_response(raw) == payload

    def test_parses_json_wrapped_in_unlabeled_code_fence(self):
        payload = {"category": "report", "confidence": 0.7}
        raw = f"```\n{json.dumps(payload)}\n```"
        assert parse_json_response(raw) == payload

    def test_strips_surrounding_whitespace(self):
        payload = {"category": "medical", "confidence": 0.6}
        raw = f"\n\n  {json.dumps(payload)}  \n\n"
        assert parse_json_response(raw) == payload

    def test_handles_prose_before_and_after_fenced_block(self):
        payload = {"category": "legal", "confidence": 0.95}
        raw = f"Here is the result:\n```json\n{json.dumps(payload)}\n```\nDone."
        assert parse_json_response(raw) == payload

    def test_raises_on_malformed_json(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json_response("this is not json at all")

    def test_raises_on_empty_string(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json_response("")
