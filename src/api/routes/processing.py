"""Processing pipeline API routes."""

import json
import logging

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.models.schemas import AnalysisResponse, EntityItem
from src.pipeline.orchestrator import process_document
from src.storage import database as db
from src.storage.minio_client import download_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["processing"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/{document_id}/process")
@limiter.limit("3/minute")
async def trigger_processing(request: Request, document_id: str):
    """Trigger the full IDP pipeline for a document."""
    row = await db.fetchrow("SELECT * FROM documents WHERE id = $1", document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    if row["status"] == "processing":
        raise HTTPException(status_code=409, detail="Document is already being processed")

    # Download PDF from MinIO
    pdf_bytes = download_file(row["storage_key"])

    # Run the pipeline
    result = await process_document(document_id, pdf_bytes)

    return {
        "document_id": document_id,
        "status": "completed" if not result.requires_review else "review_needed",
        "confidence_tier": result.confidence_tier,
        "overall_confidence": result.overall_confidence,
        "category": result.category,
        "summary": result.summary,
        "processing_duration_ms": int((result.tokens_used or 0) * 0.1),
        "tokens_used": result.tokens_used,
    }


@router.get("/{document_id}/status")
async def get_processing_status(document_id: str):
    """Get the processing status of a document."""
    row = await db.fetchrow("SELECT status, page_count FROM documents WHERE id = $1", document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    analysis = await db.fetchrow(
        """SELECT confidence_tier, overall_confidence, processing_duration_ms
           FROM document_analysis WHERE document_id = $1""",
        document_id,
    )

    return {
        "document_id": document_id,
        "status": row["status"],
        "page_count": row["page_count"],
        "confidence_tier": analysis["confidence_tier"] if analysis else None,
        "overall_confidence": analysis["overall_confidence"] if analysis else None,
        "processing_duration_ms": analysis["processing_duration_ms"] if analysis else None,
    }


@router.get("/{document_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(document_id: str):
    """Get the full analysis results for a document."""
    row = await db.fetchrow(
        "SELECT * FROM document_analysis WHERE document_id = $1",
        document_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Parse JSON fields
    entities_raw = row["key_entities"]
    if isinstance(entities_raw, str):
        entities_raw = json.loads(entities_raw)

    terms_raw = row["key_terms"]
    if isinstance(terms_raw, str):
        terms_raw = json.loads(terms_raw)

    entities = [EntityItem(**e) for e in (entities_raw or [])]

    return AnalysisResponse(
        id=row["id"],
        document_id=row["document_id"],
        category=row["category"],
        category_confidence=row["category_confidence"],
        title=row["title"],
        author=row["author"],
        document_date=row["document_date"],
        language=row["language"],
        summary=row["summary"],
        key_entities=entities,
        key_terms=terms_raw or [],
        quality_score=row["quality_score"],
        readability_score=row["readability_score"],
        completeness_score=row["completeness_score"],
        structure_score=row["structure_score"],
        overall_confidence=row["overall_confidence"],
        confidence_tier=row["confidence_tier"],
        requires_review=row["requires_review"],
        ocr_applied=row["ocr_applied"],
        ocr_confidence=row["ocr_confidence"],
        processing_duration_ms=row["processing_duration_ms"],
        llm_tokens_used=row["llm_tokens_used"],
        llm_cost_estimate=row["llm_cost_estimate"],
        created_at=row["created_at"],
    )
