"""Confidence threshold management and intelligent routing logic.

This module implements a weighted confidence scoring system that aggregates
confidence from multiple pipeline stages and routes documents to the appropriate
processing tier (HIGH/MEDIUM/LOW) for automated or human review.
"""

import logging
from dataclasses import dataclass

from src.config import settings

logger = logging.getLogger(__name__)

# Weights for each pipeline stage in overall confidence calculation
STAGE_WEIGHTS = {
    "classification": 0.25,
    "extraction": 0.30,
    "ocr": 0.20,
    "quality": 0.25,
}


@dataclass
class RoutingDecision:
    """Result of the confidence routing logic."""

    overall_confidence: float
    confidence_tier: str  # HIGH, MEDIUM, LOW
    requires_review: bool
    stage_confidences: dict  # Per-stage confidence breakdown
    low_confidence_stages: list[str]  # Stages below MEDIUM threshold
    routing_explanation: str


def calculate_overall_confidence(
    classification_confidence: float,
    extraction_confidence: float,
    ocr_confidence: float | None,
    quality_score: float,
) -> dict[str, float]:
    """Calculate weighted overall confidence from pipeline stages.

    Args:
        classification_confidence: Confidence from document classification (0-1)
        extraction_confidence: Average confidence from metadata extraction (0-1)
        ocr_confidence: OCR confidence if applied, None if not needed
        quality_score: Overall quality assessment score (0-1)

    Returns:
        Dict with per-stage and overall confidence values.
    """
    stages = {
        "classification": classification_confidence,
        "extraction": extraction_confidence,
        "quality": quality_score,
    }

    # If OCR was applied, use its confidence; otherwise redistribute weight
    if ocr_confidence is not None:
        stages["ocr"] = ocr_confidence
        weights = STAGE_WEIGHTS.copy()
    else:
        # Redistribute OCR weight proportionally to other stages
        ocr_weight = STAGE_WEIGHTS["ocr"]
        remaining_weight = 1.0 - ocr_weight
        weights = {k: v / remaining_weight for k, v in STAGE_WEIGHTS.items() if k != "ocr"}

    # Calculate weighted average
    overall = sum(stages[k] * weights[k] for k in stages)

    return {**stages, "overall": round(overall, 4)}


def route_document(
    classification_confidence: float,
    extraction_confidence: float,
    ocr_confidence: float | None,
    quality_score: float,
) -> RoutingDecision:
    """Route a document based on confidence thresholds.

    Implements 3-tier routing:
    - HIGH (>= 0.85): Auto-accept all extractions
    - MEDIUM (0.60-0.85): Flag for review, highlight uncertain fields
    - LOW (< 0.60): Queue for human review

    Args:
        classification_confidence: Classification stage confidence
        extraction_confidence: Extraction stage confidence
        ocr_confidence: OCR confidence (None if not applied)
        quality_score: Quality assessment score

    Returns:
        RoutingDecision with tier, review status, and explanation.
    """
    high_threshold = settings.confidence_high_threshold
    medium_threshold = settings.confidence_medium_threshold

    confidences = calculate_overall_confidence(
        classification_confidence, extraction_confidence, ocr_confidence, quality_score
    )

    overall = confidences["overall"]

    # Identify low-confidence stages
    low_stages = []
    for stage, conf in confidences.items():
        if stage == "overall":
            continue
        if conf < medium_threshold:
            low_stages.append(stage)

    # Determine tier
    if overall >= high_threshold and not low_stages:
        tier = "HIGH"
        requires_review = False
        explanation = (
            f"All pipeline stages passed with high confidence (overall: {overall:.2f}). "
            f"Results auto-accepted."
        )
    elif overall >= medium_threshold:
        tier = "MEDIUM"
        requires_review = True
        if low_stages:
            explanation = (
                f"Overall confidence is acceptable ({overall:.2f}) but "
                f"stages [{', '.join(low_stages)}] have low confidence. "
                f"Flagged for review."
            )
        else:
            explanation = (
                f"Overall confidence ({overall:.2f}) is between thresholds. Flagged for review."
            )
    else:
        tier = "LOW"
        requires_review = True
        explanation = (
            f"Overall confidence is low ({overall:.2f}). "
            f"Stages with issues: [{', '.join(low_stages) or 'all stages'}]. "
            f"Queued for human review."
        )

    logger.info(f"Routing decision: tier={tier}, overall={overall:.3f}, low_stages={low_stages}")

    return RoutingDecision(
        overall_confidence=overall,
        confidence_tier=tier,
        requires_review=requires_review,
        stage_confidences=confidences,
        low_confidence_stages=low_stages,
        routing_explanation=explanation,
    )
