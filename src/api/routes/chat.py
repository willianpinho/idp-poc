"""Chat Q&A API routes."""

import json
import logging

from fastapi import APIRouter, HTTPException

from src.models.schemas import ChatMessageResponse, ChatRequest, ChatResponse, ChatSource
from src.rag.chat import ask_question
from src.storage import database as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["chat"])


@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(document_id: str, request: ChatRequest):
    """Ask a question about a document using RAG."""
    # Verify document exists and is processed
    row = await db.fetchrow("SELECT status FROM documents WHERE id = $1", document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    if row["status"] not in ("completed", "review_needed"):
        raise HTTPException(
            status_code=400,
            detail=f"Document is not processed yet (status: {row['status']})",
        )

    response = await ask_question(document_id, request.question)
    return response


@router.get("/{document_id}/chat/history", response_model=list[ChatMessageResponse])
async def get_chat_history(document_id: str):
    """Get chat history for a document."""
    row = await db.fetchrow("SELECT id FROM documents WHERE id = $1", document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    rows = await db.fetch(
        """SELECT * FROM chat_messages
           WHERE document_id = $1
           ORDER BY created_at ASC""",
        document_id,
    )

    results = []
    for r in rows:
        sources_raw = r["sources"]
        if isinstance(sources_raw, str):
            sources_raw = json.loads(sources_raw)
        sources = [ChatSource(**s) for s in (sources_raw or [])]

        results.append(ChatMessageResponse(
            id=r["id"],
            document_id=r["document_id"],
            role=r["role"],
            content=r["content"],
            sources=sources,
            created_at=r["created_at"],
        ))

    return results
