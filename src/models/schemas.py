from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# --- Document Schemas ---


class DocumentCreate(BaseModel):
    filename: str
    original_filename: str
    mime_type: str = "application/pdf"
    file_size_bytes: int
    storage_key: str


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    page_count: int | None
    storage_key: str
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


# --- Analysis Schemas ---


class EntityItem(BaseModel):
    name: str
    type: str
    confidence: float


class ConfidenceField(BaseModel):
    value: str | None
    confidence: float


class AnalysisResponse(BaseModel):
    id: UUID
    document_id: UUID
    category: str | None
    category_confidence: float | None
    title: str | None
    author: str | None
    document_date: str | None
    language: str | None
    summary: str | None
    key_entities: list[EntityItem] = []
    key_terms: list[str] = []
    quality_score: float | None
    readability_score: float | None
    completeness_score: float | None
    structure_score: float | None
    overall_confidence: float | None
    confidence_tier: str | None
    requires_review: bool
    ocr_applied: bool
    ocr_confidence: float | None
    processing_duration_ms: int | None
    llm_tokens_used: int | None
    llm_cost_estimate: float | None
    created_at: datetime


# --- Chat Schemas ---


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class ChatSource(BaseModel):
    chunk_id: str
    page_numbers: list[int]
    relevance_score: float
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = []
    confidence: str = "medium"


class ChatMessageResponse(BaseModel):
    id: UUID
    document_id: UUID
    role: str
    content: str
    sources: list[ChatSource] = []
    created_at: datetime


# --- Review Schemas ---


class ReviewUpdateRequest(BaseModel):
    review_notes: str | None = None
    approved: bool = False


# --- Processing Schemas ---


class ProcessingStatusResponse(BaseModel):
    document_id: UUID
    status: str
    pipeline_stages: dict = {}


# --- Pipeline Internal Models ---


class PipelineResult(BaseModel):
    """Result from the full processing pipeline."""

    text_content: str = ""
    page_count: int = 0
    ocr_applied: bool = False
    ocr_confidence: float | None = None
    ocr_pages: list[int] = []
    category: str | None = None
    category_confidence: float = 0.0
    title: str | None = None
    author: str | None = None
    document_date: str | None = None
    language: str | None = None
    summary: str | None = None
    key_entities: list[EntityItem] = []
    key_terms: list[str] = []
    quality_score: float = 0.0
    readability_score: float = 0.0
    completeness_score: float = 0.0
    structure_score: float = 0.0
    overall_confidence: float = 0.0
    confidence_tier: str = "LOW"
    requires_review: bool = True
    tokens_used: int = 0
    cost_estimate: float = 0.0
    extraction_confidence: float = 0.0
