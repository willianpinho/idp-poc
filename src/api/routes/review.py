"""Review queue API routes."""

import logging

from fastapi import APIRouter, HTTPException

from src.models.schemas import ReviewUpdateRequest
from src.storage import database as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/queue")
async def get_review_queue():
    """Get documents needing human review, sorted by confidence (lowest first)."""
    rows = await db.fetch(
        """SELECT d.id as document_id, d.filename, d.original_filename,
                  d.status, d.page_count, d.created_at,
                  a.id as analysis_id, a.category, a.category_confidence,
                  a.title, a.summary,
                  a.overall_confidence, a.confidence_tier,
                  a.requires_review, a.review_notes,
                  a.ocr_applied, a.ocr_confidence,
                  a.processing_duration_ms
           FROM documents d
           JOIN document_analysis a ON d.id = a.document_id
           WHERE a.requires_review = true
           ORDER BY a.overall_confidence ASC"""
    )

    return {
        "items": [dict(r) for r in rows],
        "total": len(rows),
    }


@router.patch("/{analysis_id}")
async def update_review(analysis_id: str, request: ReviewUpdateRequest):
    """Update review status for a document analysis."""
    row = await db.fetchrow("SELECT document_id FROM document_analysis WHERE id = $1", analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if request.approved:
        # Mark as reviewed and approved
        await db.execute(
            """UPDATE document_analysis
               SET requires_review = false, review_notes = $1
               WHERE id = $2""",
            request.review_notes,
            analysis_id,
        )
        await db.execute(
            "UPDATE documents SET status = 'completed', updated_at = NOW() WHERE id = $1",
            row["document_id"],
        )
        logger.info(f"Analysis {analysis_id} approved")
    else:
        # Update review notes only
        await db.execute(
            "UPDATE document_analysis SET review_notes = $1 WHERE id = $2",
            request.review_notes,
            analysis_id,
        )

    return {"status": "updated", "analysis_id": analysis_id}
