"""LLM-based document quality assessment using Anthropic Claude."""

import json
import logging
from dataclasses import dataclass, field

import anthropic

from src.config import settings

logger = logging.getLogger(__name__)

QUALITY_PROMPT = """Assess the quality of the following document text.

Evaluate these dimensions on a scale of 0.0 to 1.0:
- readability: How clear and readable is the text? (grammar, clarity, formatting)
- completeness: Does the document appear complete? (vs truncated, partial, or fragmentary)
- structure: Does it have clear structure? (headings, sections, logical flow)
- overall: Overall document quality score

Return ONLY a valid JSON object:
{{
  "readability": 0.0-1.0,
  "completeness": 0.0-1.0,
  "structure": 0.0-1.0,
  "overall": 0.0-1.0,
  "issues": ["list of quality issues found, if any"]
}}

Document text (first 4000 characters):
---
{text}
---

Return only the JSON object, no other text."""


@dataclass
class QualityResult:
    readability: float = 0.0
    completeness: float = 0.0
    structure: float = 0.0
    overall: float = 0.0
    issues: list[str] = field(default_factory=list)
    tokens_used: int = 0


def assess_quality(text: str) -> QualityResult:
    """Assess document quality using Claude."""
    if not settings.anthropic_api_key:
        logger.warning("No Anthropic API key, returning default quality")
        return QualityResult(
            readability=0.5, completeness=0.5, structure=0.5, overall=0.5
        )

    truncated = text[:4000]
    prompt = QUALITY_PROMPT.format(text=truncated)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    raw = response.content[0].text.strip()

    try:
        from src.pipeline.llm_utils import parse_json_response

        data = parse_json_response(raw)
        return QualityResult(
            readability=float(data.get("readability", 0.5)),
            completeness=float(data.get("completeness", 0.5)),
            structure=float(data.get("structure", 0.5)),
            overall=float(data.get("overall", 0.5)),
            issues=data.get("issues", []),
            tokens_used=tokens_used,
        )
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse quality response: {e}")
        return QualityResult(tokens_used=tokens_used)
