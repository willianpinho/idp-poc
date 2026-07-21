"""Tests for the weighted confidence aggregation and 3-tier routing logic."""

from src.pipeline.confidence_router import calculate_overall_confidence, route_document


class TestCalculateOverallConfidence:
    def test_weighted_average_with_ocr(self):
        result = calculate_overall_confidence(
            classification_confidence=0.8,
            extraction_confidence=0.6,
            ocr_confidence=0.4,
            quality_score=0.9,
        )

        expected = 0.8 * 0.25 + 0.6 * 0.30 + 0.4 * 0.20 + 0.9 * 0.25
        assert result["overall"] == round(expected, 4)
        assert result["classification"] == 0.8
        assert result["extraction"] == 0.6
        assert result["ocr"] == 0.4
        assert result["quality"] == 0.9

    def test_ocr_weight_is_redistributed_when_ocr_not_applied(self):
        result = calculate_overall_confidence(
            classification_confidence=0.8,
            extraction_confidence=0.6,
            ocr_confidence=None,
            quality_score=0.9,
        )

        # OCR's 0.20 weight is redistributed proportionally across the other
        # three stages, so "ocr" must not appear in the result at all.
        assert "ocr" not in result

        remaining = 1.0 - 0.20
        expected = 0.8 * (0.25 / remaining) + 0.6 * (0.30 / remaining) + 0.9 * (0.25 / remaining)
        assert result["overall"] == round(expected, 4)

    def test_uniform_confidence_produces_same_overall_value(self):
        # When every stage reports the same confidence, the weighted average
        # must equal that value regardless of the per-stage weights.
        result = calculate_overall_confidence(
            classification_confidence=0.73,
            extraction_confidence=0.73,
            ocr_confidence=0.73,
            quality_score=0.73,
        )
        assert result["overall"] == 0.73


class TestRouteDocumentTiers:
    def test_high_tier_when_all_stages_strong(self):
        decision = route_document(
            classification_confidence=0.9,
            extraction_confidence=0.9,
            ocr_confidence=0.9,
            quality_score=0.9,
        )
        assert decision.confidence_tier == "HIGH"
        assert decision.requires_review is False
        assert decision.low_confidence_stages == []
        assert decision.overall_confidence == 0.9

    def test_medium_tier_when_overall_between_thresholds(self):
        decision = route_document(
            classification_confidence=0.70,
            extraction_confidence=0.70,
            ocr_confidence=0.70,
            quality_score=0.70,
        )
        assert decision.confidence_tier == "MEDIUM"
        assert decision.requires_review is True
        assert decision.low_confidence_stages == []
        assert "between thresholds" in decision.routing_explanation

    def test_low_tier_when_overall_below_medium_threshold(self):
        decision = route_document(
            classification_confidence=0.2,
            extraction_confidence=0.2,
            ocr_confidence=0.2,
            quality_score=0.2,
        )
        assert decision.confidence_tier == "LOW"
        assert decision.requires_review is True
        # Every stage is below the medium threshold, in insertion order.
        assert decision.low_confidence_stages == [
            "classification",
            "extraction",
            "quality",
            "ocr",
        ]

    def test_high_overall_downgraded_to_medium_by_one_weak_stage(self):
        # Overall confidence clears the HIGH bar, but OCR alone is unreliable
        # -- the router must not auto-accept a document with a genuinely weak
        # stage just because the weighted average looks good.
        decision = route_document(
            classification_confidence=1.0,
            extraction_confidence=1.0,
            ocr_confidence=0.5,
            quality_score=1.0,
        )
        assert decision.overall_confidence >= 0.85
        assert decision.confidence_tier == "MEDIUM"
        assert decision.requires_review is True
        assert decision.low_confidence_stages == ["ocr"]
        assert "ocr" in decision.routing_explanation

    def test_route_document_without_ocr_never_flags_ocr_as_low(self):
        decision = route_document(
            classification_confidence=0.3,
            extraction_confidence=0.3,
            ocr_confidence=None,
            quality_score=0.3,
        )
        assert "ocr" not in decision.stage_confidences
        assert "ocr" not in decision.low_confidence_stages


class TestRouteDocumentBoundaries:
    def test_boundary_exactly_at_high_threshold_is_high(self):
        decision = route_document(0.85, 0.85, 0.85, 0.85)
        assert decision.confidence_tier == "HIGH"

    def test_boundary_just_below_high_threshold_is_medium(self):
        decision = route_document(0.8499, 0.8499, 0.8499, 0.8499)
        assert decision.confidence_tier == "MEDIUM"

    def test_boundary_exactly_at_medium_threshold_is_medium(self):
        decision = route_document(0.60, 0.60, 0.60, 0.60)
        assert decision.confidence_tier == "MEDIUM"

    def test_boundary_just_below_medium_threshold_is_low(self):
        decision = route_document(0.5999, 0.5999, 0.5999, 0.5999)
        assert decision.confidence_tier == "LOW"
