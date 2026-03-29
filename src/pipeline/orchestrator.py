"""Main pipeline orchestrator — coordinates all processing stages."""

import json
import logging
import time
from datetime import datetime, timezone

from src.models.schemas import PipelineResult
from src.pipeline.chunker import chunk_text
from src.pipeline.classifier import classify_document
from src.pipeline.confidence_router import route_document
from src.pipeline.embedder import generate_embedding
from src.pipeline.extractor import extract_metadata
from src.pipeline.ocr_engine import run_ocr
from src.pipeline.pdf_parser import parse_pdf
from src.pipeline.quality_assessor import assess_quality
from src.storage import database as db

logger = logging.getLogger(__name__)


async def process_document(document_id: str, pdf_bytes: bytes) -> PipelineResult:
    """Run the full IDP pipeline on a document.

    Pipeline stages:
    1. PDF Parsing (pypdf)
    2. OCR (pytesseract, only for pages without text)
    3. Content Merge (best source per page)
    4. Classification (Claude)
    5. Metadata Extraction (Claude)
    6. Quality Assessment (Claude)
    7. Confidence Routing (threshold-based)
    8. Chunking (sliding window)
    9. Embeddings (hash-based / Voyage)
    10. Store Results (PostgreSQL + pgvector)

    Args:
        document_id: UUID of the document to process.
        pdf_bytes: Raw PDF file bytes.

    Returns:
        PipelineResult with all extracted data and confidence scores.
    """
    start_time = time.time()
    result = PipelineResult()
    total_tokens = 0

    # Update status to processing
    await db.execute(
        "UPDATE documents SET status = 'processing', updated_at = NOW() WHERE id = $1",
        document_id,
    )

    try:
        # --- Stage 1: PDF Parsing ---
        logger.info(f"[{document_id}] Stage 1: PDF Parsing")
        parsed = parse_pdf(pdf_bytes)
        result.page_count = parsed.page_count

        # --- Stage 2: OCR for pages without text ---
        logger.info(f"[{document_id}] Stage 2: OCR")
        pages_needing_ocr = [i for i, has_text in enumerate(parsed.has_text) if not has_text]

        ocr_text_by_page: dict[int, str] = {}
        if pages_needing_ocr:
            ocr_result = run_ocr(pdf_bytes, pages_needing_ocr)
            result.ocr_applied = ocr_result.applied
            result.ocr_confidence = ocr_result.average_confidence
            result.ocr_pages = ocr_result.pages_applied
            for ocr_page in ocr_result.pages:
                ocr_text_by_page[ocr_page.page_number] = ocr_page.text
        else:
            result.ocr_applied = False
            result.ocr_confidence = None

        # --- Stage 3: Content Merge ---
        logger.info(f"[{document_id}] Stage 3: Content Merge")
        final_pages = []
        for i, page_text in enumerate(parsed.pages):
            if parsed.has_text[i]:
                final_pages.append(page_text)
            elif i in ocr_text_by_page:
                final_pages.append(ocr_text_by_page[i])
            else:
                final_pages.append(page_text)

        result.text_content = "\n\n".join(final_pages)

        if not result.text_content.strip():
            logger.warning(f"[{document_id}] No text content extracted")
            await _save_error(document_id, "No text content could be extracted from PDF")
            result.confidence_tier = "LOW"
            result.requires_review = True
            return result

        # --- Stage 4: Classification ---
        logger.info(f"[{document_id}] Stage 4: Classification")
        classification = classify_document(result.text_content)
        result.category = classification.category
        result.category_confidence = classification.confidence
        total_tokens += classification.tokens_used

        # --- Stage 5: Metadata Extraction ---
        logger.info(f"[{document_id}] Stage 5: Extraction")
        extraction = extract_metadata(result.text_content)
        result.title = extraction.title
        result.author = extraction.author
        result.document_date = extraction.document_date
        result.language = extraction.language
        result.summary = extraction.summary
        result.key_entities = extraction.key_entities
        result.key_terms = extraction.key_terms
        result.extraction_confidence = extraction.average_confidence
        total_tokens += extraction.tokens_used

        # --- Stage 6: Quality Assessment ---
        logger.info(f"[{document_id}] Stage 6: Quality Assessment")
        quality = assess_quality(result.text_content)
        result.quality_score = quality.overall
        result.readability_score = quality.readability
        result.completeness_score = quality.completeness
        result.structure_score = quality.structure
        total_tokens += quality.tokens_used

        # --- Stage 7: Confidence Routing ---
        logger.info(f"[{document_id}] Stage 7: Confidence Routing")
        routing = route_document(
            classification_confidence=result.category_confidence,
            extraction_confidence=result.extraction_confidence,
            ocr_confidence=result.ocr_confidence,
            quality_score=result.quality_score,
        )
        result.overall_confidence = routing.overall_confidence
        result.confidence_tier = routing.confidence_tier
        result.requires_review = routing.requires_review

        # --- Stage 8: Chunking ---
        logger.info(f"[{document_id}] Stage 8: Chunking")
        chunks = chunk_text(final_pages)

        # --- Stage 9: Embeddings ---
        logger.info(f"[{document_id}] Stage 9: Embeddings")
        for chunk in chunks:
            chunk_embedding = generate_embedding(chunk.content)
            # pgvector expects string format: '[0.1, 0.2, ...]'
            embedding_str = "[" + ",".join(str(v) for v in chunk_embedding) + "]"

            await db.execute(
                """INSERT INTO document_chunks
                   (document_id, chunk_index, content, page_numbers, token_count, embedding)
                   VALUES ($1, $2, $3, $4, $5, $6::vector)""",
                document_id,
                chunk.index,
                chunk.content,
                chunk.page_numbers,
                chunk.token_count,
                embedding_str,
            )

        # --- Stage 10: Store Results ---
        logger.info(f"[{document_id}] Stage 10: Store Results")
        duration_ms = int((time.time() - start_time) * 1000)
        result.tokens_used = total_tokens
        result.cost_estimate = total_tokens * 0.000003  # Rough estimate

        await db.execute(
            """INSERT INTO document_analysis
               (document_id, category, category_confidence,
                title, author, document_date, language, summary,
                key_entities, key_terms, extracted_metadata,
                quality_score, readability_score, completeness_score, structure_score,
                quality_details,
                overall_confidence, confidence_tier, requires_review,
                ocr_applied, ocr_confidence, ocr_engine, pages_ocr_applied,
                processing_started_at, processing_completed_at,
                processing_duration_ms, llm_tokens_used, llm_cost_estimate)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,
                       $15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28)""",
            document_id,
            result.category,
            result.category_confidence,
            result.title,
            result.author,
            result.document_date,
            result.language,
            result.summary,
            json.dumps([e.model_dump() for e in result.key_entities]),
            json.dumps(result.key_terms),
            json.dumps(extraction.raw_response),
            result.quality_score,
            result.readability_score,
            result.completeness_score,
            result.structure_score,
            json.dumps({"issues": quality.issues}),
            result.overall_confidence,
            result.confidence_tier,
            result.requires_review,
            result.ocr_applied,
            result.ocr_confidence,
            "tesseract" if result.ocr_applied else None,
            result.ocr_pages if result.ocr_pages else None,
            datetime.fromtimestamp(start_time, tz=timezone.utc),
            datetime.now(tz=timezone.utc),
            duration_ms,
            total_tokens,
            result.cost_estimate,
        )

        # Update document status
        new_status = "completed" if not result.requires_review else "review_needed"
        await db.execute(
            """UPDATE documents
               SET status = $1, page_count = $2, updated_at = NOW()
               WHERE id = $3""",
            new_status,
            result.page_count,
            document_id,
        )

        logger.info(
            f"[{document_id}] Pipeline complete: tier={result.confidence_tier}, "
            f"duration={duration_ms}ms, tokens={total_tokens}"
        )

        return result

    except Exception as e:
        logger.error(f"[{document_id}] Pipeline error: {e}", exc_info=True)
        await _save_error(document_id, str(e))
        raise


async def _save_error(document_id: str, error: str):
    await db.execute(
        "UPDATE documents SET status = 'failed', updated_at = NOW() WHERE id = $1",
        document_id,
    )
    await db.execute(
        """INSERT INTO document_analysis (document_id, error_log, confidence_tier, requires_review)
           VALUES ($1, $2, 'LOW', true)
           ON CONFLICT DO NOTHING""",
        document_id,
        error,
    )
