"""Document CRUD API routes."""

import logging
import uuid

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.models.schemas import DocumentListResponse, DocumentResponse
from src.storage import database as db
from src.storage.minio_client import delete_file, get_presigned_url, upload_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])

MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=DocumentResponse, status_code=201)
@limiter.limit("5/minute")
async def upload_document(request: Request, file: UploadFile = File(...)):
    """Upload a PDF document.

    Stores the file in MinIO and creates a database record.
    Limited to 20MB per file, 5 uploads per minute.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(content) > MAX_UPLOAD_SIZE:
        max_mb = MAX_UPLOAD_SIZE // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {max_mb}MB")

    doc_id = str(uuid.uuid4())
    storage_key = f"originals/{doc_id}/{file.filename}"

    # Upload to MinIO
    upload_file(storage_key, content, content_type="application/pdf")

    # Create database record
    row = await db.fetchrow(
        """INSERT INTO documents (
               id, filename, original_filename, mime_type,
               file_size_bytes, storage_key, status)
           VALUES ($1, $2, $3, $4, $5, $6, 'uploaded')
           RETURNING *""",
        doc_id,
        file.filename,
        file.filename,
        "application/pdf",
        len(content),
        storage_key,
    )

    logger.info(f"Document uploaded: {doc_id} ({file.filename}, {len(content)} bytes)")
    return _row_to_response(row)


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """List all documents."""
    rows = await db.fetch("SELECT * FROM documents ORDER BY created_at DESC")
    return DocumentListResponse(
        documents=[_row_to_response(r) for r in rows],
        total=len(rows),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get a single document by ID."""
    row = await db.fetchrow("SELECT * FROM documents WHERE id = $1", document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    return _row_to_response(row)


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: str):
    """Delete a document and all related data."""
    row = await db.fetchrow("SELECT storage_key FROM documents WHERE id = $1", document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from MinIO
    delete_file(row["storage_key"])

    # Delete from DB (cascades to analysis, chunks, chat)
    await db.execute("DELETE FROM documents WHERE id = $1", document_id)
    logger.info(f"Document deleted: {document_id}")


@router.get("/{document_id}/download")
async def download_document(document_id: str):
    """Get a presigned download URL for the document."""
    row = await db.fetchrow("SELECT storage_key FROM documents WHERE id = $1", document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    url = get_presigned_url(row["storage_key"])
    return {"download_url": url}


def _row_to_response(row) -> DocumentResponse:
    return DocumentResponse(
        id=row["id"],
        filename=row["filename"],
        original_filename=row["original_filename"],
        mime_type=row["mime_type"],
        file_size_bytes=row["file_size_bytes"],
        page_count=row["page_count"],
        storage_key=row["storage_key"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
