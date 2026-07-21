"""Shared pytest fixtures for the idp-app test suite.

Every fixture here mocks external I/O (Anthropic, Voyage AI HTTP calls) so the
suite runs fully offline and deterministically — no live API calls, no network,
no database, no MinIO.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.config import settings


def make_anthropic_response(
    text: str, input_tokens: int = 100, output_tokens: int = 50
) -> SimpleNamespace:
    """Build a fake Anthropic Messages.create() response object."""
    return SimpleNamespace(
        content=[SimpleNamespace(text=text)],
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


@pytest.fixture
def anthropic_api_key(monkeypatch):
    """Give settings a fake API key so pipeline stages don't short-circuit
    into their "no API key configured" default-response path."""
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-ant-test-key")


@pytest.fixture
def mock_anthropic(monkeypatch):
    """Factory fixture: patch the `anthropic` module reference used inside a
    given pipeline module so `anthropic.Anthropic(...).messages.create(...)`
    returns a canned response, without ever contacting the real API.

    Usage:
        client = mock_anthropic("src.pipeline.classifier", '{"category": "invoice"}')
    """

    def _patch(module_path: str, response_text: str, **usage_kwargs) -> MagicMock:
        fake_client = MagicMock()
        fake_client.messages.create.return_value = make_anthropic_response(
            response_text, **usage_kwargs
        )
        fake_anthropic_module = MagicMock()
        fake_anthropic_module.Anthropic.return_value = fake_client
        monkeypatch.setattr(f"{module_path}.anthropic", fake_anthropic_module)
        return fake_client

    return _patch
