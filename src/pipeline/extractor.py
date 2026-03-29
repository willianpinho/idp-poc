"""LLM-based structured metadata extraction using Anthropic Claude."""

import json
import logging
from dataclasses import dataclass, field

import anthropic

from src.config import settings
from src.models.schemas import EntityItem

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extract structured metadata from the following document text.

Return ONLY a valid JSON object with these fields:
{{
  "title": {{"value": "document title or null", "confidence": 0.0-1.0}},
  "author": {{"value": "author name or null", "confidence": 0.0-1.0}},
  "date": {{"value": "ISO date string or null", "confidence": 0.0-1.0}},
  "language": {{"value": "ISO 639-1 code (e.g. en, pt, es)", "confidence": 0.0-1.0}},
  "summary": {{"value": "2-3 sentence summary of the document", "confidence": 0.0-1.0}},
  "key_entities": [
    {{"name": "entity name", "type": "person|org|location|date|amount|other",
      "confidence": 0.0-1.0}}
  ],
  "key_terms": ["term1", "term2", "term3"]
}}

Rules:
- Set confidence to how certain you are about each extracted field
- If a field cannot be determined, set value to null and confidence to 0.0
- Extract up to 10 key entities and 10 key terms
- Summary should capture the main purpose and content of the document

Document text (first 6000 characters):
---
{text}
---

Return only the JSON object, no other text."""


@dataclass
class ExtractionResult:
    title: str | None = None
    title_confidence: float = 0.0
    author: str | None = None
    author_confidence: float = 0.0
    document_date: str | None = None
    date_confidence: float = 0.0
    language: str | None = None
    language_confidence: float = 0.0
    summary: str | None = None
    summary_confidence: float = 0.0
    key_entities: list[EntityItem] = field(default_factory=list)
    key_terms: list[str] = field(default_factory=list)
    tokens_used: int = 0
    raw_response: dict = field(default_factory=dict)

    @property
    def average_confidence(self) -> float:
        confidences = [
            self.title_confidence,
            self.author_confidence,
            self.date_confidence,
            self.language_confidence,
            self.summary_confidence,
        ]
        non_zero = [c for c in confidences if c > 0]
        return sum(non_zero) / len(non_zero) if non_zero else 0.0


def extract_metadata(text: str) -> ExtractionResult:
    """Extract structured metadata from document text using Claude."""
    if not settings.anthropic_api_key:
        logger.warning("No Anthropic API key, returning empty extraction")
        return ExtractionResult()

    truncated = text[:6000]
    prompt = EXTRACTION_PROMPT.format(text=truncated)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    raw = response.content[0].text.strip()

    try:
        from src.pipeline.llm_utils import parse_json_response

        data = parse_json_response(raw)
        result = ExtractionResult(tokens_used=tokens_used, raw_response=data)

        # Parse title
        title_data = data.get("title", {})
        result.title = title_data.get("value")
        result.title_confidence = float(title_data.get("confidence", 0.0))

        # Parse author
        author_data = data.get("author", {})
        result.author = author_data.get("value")
        result.author_confidence = float(author_data.get("confidence", 0.0))

        # Parse date
        date_data = data.get("date", {})
        result.document_date = date_data.get("value")
        result.date_confidence = float(date_data.get("confidence", 0.0))

        # Parse language
        lang_data = data.get("language", {})
        result.language = lang_data.get("value")
        result.language_confidence = float(lang_data.get("confidence", 0.0))

        # Parse summary
        summary_data = data.get("summary", {})
        result.summary = summary_data.get("value")
        result.summary_confidence = float(summary_data.get("confidence", 0.0))

        # Parse entities
        for entity in data.get("key_entities", [])[:10]:
            result.key_entities.append(
                EntityItem(
                    name=entity.get("name", ""),
                    type=entity.get("type", "other"),
                    confidence=float(entity.get("confidence", 0.5)),
                )
            )

        # Parse key terms
        result.key_terms = data.get("key_terms", [])[:10]

        return result

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse extraction response: {e}")
        return ExtractionResult(tokens_used=tokens_used)
