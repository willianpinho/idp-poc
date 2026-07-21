"""Tests for Pydantic request/response schema validation and defaults."""

import pytest
from pydantic import ValidationError

from src.models.schemas import ChatRequest, EntityItem, PipelineResult


class TestChatRequestValidation:
    def test_accepts_a_valid_question(self):
        req = ChatRequest(question="What is the contract value?")
        assert req.question == "What is the contract value?"

    def test_rejects_empty_question(self):
        with pytest.raises(ValidationError):
            ChatRequest(question="")

    def test_rejects_question_over_max_length(self):
        with pytest.raises(ValidationError):
            ChatRequest(question="x" * 2001)

    def test_accepts_question_at_max_length(self):
        req = ChatRequest(question="x" * 2000)
        assert len(req.question) == 2000


class TestPipelineResultDefaults:
    def test_defaults_route_to_low_confidence_and_review(self):
        result = PipelineResult()
        assert result.confidence_tier == "LOW"
        assert result.requires_review is True
        assert result.overall_confidence == 0.0

    def test_default_mutable_fields_are_not_shared_between_instances(self):
        first = PipelineResult()
        second = PipelineResult()

        first.key_terms.append("mutated")
        first.key_entities.append(EntityItem(name="Acme", type="organization", confidence=0.9))

        assert second.key_terms == []
        assert second.key_entities == []


class TestEntityItem:
    def test_requires_confidence_to_be_a_float(self):
        with pytest.raises(ValidationError):
            EntityItem(name="Acme", type="organization", confidence="high")

    def test_valid_entity_item(self):
        entity = EntityItem(name="Acme Corp", type="organization", confidence=0.87)
        assert entity.name == "Acme Corp"
        assert entity.confidence == 0.87
