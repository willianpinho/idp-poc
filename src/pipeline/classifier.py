"""LLM-based document classification using Anthropic Claude."""

import json
import logging
from dataclasses import dataclass

import anthropic

from src.config import settings

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """Analyze the following document text and classify it into exactly ONE of these categories:
- contract
- invoice
- report
- legal
- medical
- academic
- correspondence
- technical
- financial
- other

Return ONLY a valid JSON object with these fields:
{{
  "category": "one of the categories above",
  "confidence": 0.0 to 1.0 (how confident you are in the classification),
  "reasoning": "brief explanation of why this category was chosen"
}}

Document text (first 4000 characters):
---
{text}
---

Return only the JSON object, no other text."""


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    reasoning: str
    tokens_used: int = 0


def classify_document(text: str) -> ClassificationResult:
    """Classify a document using Anthropic Claude."""
    if not settings.anthropic_api_key:
        logger.warning("No Anthropic API key, returning default classification")
        return ClassificationResult(
            category="other", confidence=0.0, reasoning="No API key configured"
        )

    # Truncate text to avoid token limits
    truncated = text[:4000]
    prompt = CLASSIFICATION_PROMPT.format(text=truncated)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    raw = response.content[0].text.strip()

    try:
        # Parse JSON response (handles markdown code blocks)
        from src.pipeline.llm_utils import parse_json_response

        data = parse_json_response(raw)
        return ClassificationResult(
            category=data.get("category", "other"),
            confidence=float(data.get("confidence", 0.5)),
            reasoning=data.get("reasoning", ""),
            tokens_used=tokens_used,
        )
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse classification response: {e}, raw: {raw}")
        return ClassificationResult(
            category="other",
            confidence=0.3,
            reasoning=f"Parse error: {e}",
            tokens_used=tokens_used,
        )
