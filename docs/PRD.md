# PraxisIQ - Intelligent Document Processing POC

## Product Requirements Document

**Author:** Willian Pinho
**Type:** Proof of Concept (POC)
**Status:** Draft
**Date:** 2026-03-06

---

## 1. Overview

Python-based Intelligent Document Processing (IDP) proof of concept that demonstrates a production-grade pipeline for PDF upload, AI-powered analysis, metadata extraction, OCR, classification, and conversational Q&A over documents.

**This is NOT a product** — it is a technical demonstration showcasing expertise in:

- Intelligent Document Processing (OCR, classification, extraction pipelines)
- LLM-based document understanding systems
- Confidence threshold management and intelligent routing logic
- Vector databases and embedding models
- Python AI/ML system architecture

---

## 2. Objectives

| Objective | Description |
|-----------|-------------|
| **IDP Pipeline** | End-to-end PDF processing: upload, OCR, text extraction, metadata extraction, classification |
| **LLM Understanding** | Use Anthropic Claude for document summarization, entity extraction, quality assessment |
| **Confidence Routing** | Implement confidence thresholds to route low-confidence extractions to human review |
| **Vector Search** | Store document embeddings in PostgreSQL + pgvector for semantic retrieval |
| **Conversational Q&A** | RAG-powered chat interface to ask questions about uploaded documents |
| **File Storage** | Store original PDFs and extracted assets in MinIO (S3-compatible) |

---

## 3. Architecture

```
                    +------------------+
                    |   Frontend (UI)  |
                    |   Streamlit App  |
                    +--------+---------+
                             |
                             | HTTP
                             v
                    +------------------+
                    |   FastAPI Server  |
                    |   (Python 3.12)  |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
     +--------+---+  +------+------+  +----+-------+
     |   MinIO    |  | PostgreSQL  |  |  Anthropic  |
     | (S3 store) |  | + pgvector  |  |  Claude API |
     +------------+  +-------------+  +-------------+
```

### Processing Pipeline

```
PDF Upload
    |
    v
[1. File Storage] -----> MinIO (original PDF stored)
    |
    v
[2. PDF Parsing] ------> pypdf: extract text, page count, metadata
    |
    v
[3. OCR] --------------> pytesseract + pdf2image (for scanned/image PDFs)
    |                     Confidence scoring per page
    |
    v
[4. Content Merge] ----> Merge parsed text + OCR text
    |                     Select best source per page based on confidence
    |
    v
[5. Classification] ---> Anthropic Claude: classify document type
    |                     Categories: contract, invoice, report, legal,
    |                     medical, academic, correspondence, technical, other
    |                     Returns: category + confidence score (0.0-1.0)
    |
    v
[6. Extraction] -------> Anthropic Claude: structured metadata extraction
    |                     Title, author, date, entities, key terms,
    |                     language, summary
    |                     Each field has confidence score
    |
    v
[7. Quality Assessment]-> Anthropic Claude: document quality scoring
    |                     Readability, completeness, structure quality
    |                     Overall quality score (0.0-1.0)
    |
    v
[8. Confidence Router] -> Route based on confidence thresholds:
    |                     HIGH (>= 0.85): auto-accept results
    |                     MEDIUM (0.60-0.85): flag for review
    |                     LOW (< 0.60): queue for human review
    |
    v
[9. Chunking] ---------> Split text into overlapping chunks (512 tokens, 50 overlap)
    |
    v
[10. Embeddings] -------> Anthropic/Voyage embeddings -> pgvector storage
    |
    v
[11. Store Results] ----> PostgreSQL: document record, extraction results,
                          confidence scores, processing metadata
```

---

## 4. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.12+ | Core runtime |
| **API Framework** | FastAPI | REST API with async support |
| **Frontend** | Streamlit | Simple interactive UI |
| **Database** | PostgreSQL 16 + pgvector | Relational data + vector embeddings |
| **Object Storage** | MinIO | S3-compatible PDF/image storage |
| **LLM Provider** | Anthropic Claude (claude-sonnet-4-20250514) | Classification, extraction, Q&A |
| **Embeddings** | Voyage AI (via Anthropic) or OpenAI | Document chunk embeddings |
| **OCR Engine** | pytesseract + pdf2image | Scanned document text extraction |
| **PDF Parsing** | pypdf | Native PDF text extraction |
| **Image Extraction** | pdf2image + Pillow | Extract images from PDFs |
| **Task Queue** | None (sync for POC) | Pipeline runs synchronously |
| **Package Manager** | uv | Fast Python package management |

### Reusable Modules from modules-saas-platform

| Module | Package | Usage |
|--------|---------|-------|
| `ai-core` | `msaas-ai-core` | LLM provider abstraction (Anthropic client) |
| `rag` | `msaas-rag` | Chunking, embeddings, vector search |
| `ocr` | `msaas-ocr` | Multi-engine OCR with fallback |
| `extraction` | `msaas-extraction` | LLM-based structured data extraction |
| `doc-processing` | `msaas-doc-processing` | PDF parsing, page extraction |
| `api-core` | `msaas-api-core` | Standardized API patterns |
| `db-core` | `msaas-db-core` | PostgreSQL connection pool |
| `errors` | `msaas-errors` | Standardized error handling |

> **Note:** If integrating the full module ecosystem adds too much complexity for this POC, implement simplified versions of the same patterns inline. The goal is to demonstrate the architecture, not the framework.

---

## 5. Data Model

### PostgreSQL Schema

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL DEFAULT 'application/pdf',
    file_size_bytes BIGINT NOT NULL,
    page_count INTEGER,
    storage_key VARCHAR(1000) NOT NULL,       -- MinIO object key
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    -- Status: uploaded -> processing -> processed -> review_needed -> completed -> failed
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Processing results
CREATE TABLE document_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Classification
    category VARCHAR(100),
    category_confidence FLOAT,

    -- Extracted metadata
    title VARCHAR(1000),
    author VARCHAR(500),
    document_date VARCHAR(200),
    language VARCHAR(50),
    summary TEXT,
    key_entities JSONB DEFAULT '[]',         -- [{name, type, confidence}]
    key_terms JSONB DEFAULT '[]',            -- [string]
    extracted_metadata JSONB DEFAULT '{}',   -- Full extraction output

    -- Quality assessment
    quality_score FLOAT,                     -- 0.0-1.0
    readability_score FLOAT,
    completeness_score FLOAT,
    structure_score FLOAT,
    quality_details JSONB DEFAULT '{}',

    -- Confidence routing
    overall_confidence FLOAT,                -- Weighted average
    confidence_tier VARCHAR(20),             -- HIGH, MEDIUM, LOW
    requires_review BOOLEAN DEFAULT FALSE,
    review_notes TEXT,

    -- OCR metadata
    ocr_applied BOOLEAN DEFAULT FALSE,
    ocr_confidence FLOAT,
    ocr_engine VARCHAR(50),
    pages_ocr_applied INTEGER[],             -- Which pages needed OCR

    -- Processing metadata
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    processing_duration_ms INTEGER,
    llm_tokens_used INTEGER,
    llm_cost_estimate FLOAT,
    pipeline_version VARCHAR(20) DEFAULT '1.0',
    error_log TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Document text chunks + embeddings for RAG
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_numbers INTEGER[],                  -- Source pages
    token_count INTEGER,
    embedding vector(1024),                  -- Voyage/embedding dimensions
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Vector similarity search index
CREATE INDEX idx_chunks_embedding ON document_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_analysis_document ON document_analysis(document_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_analysis_confidence ON document_analysis(confidence_tier);

-- Chat history for Q&A
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,               -- user | assistant
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]',              -- [{chunk_id, page, relevance_score}]
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### MinIO Storage Structure

```
praxisiq-bucket/
  ├── originals/
  │   └── {document_id}/{original_filename}
  ├── thumbnails/
  │   └── {document_id}/page_{n}.png
  └── extracted_images/
      └── {document_id}/img_{n}.png
```

---

## 6. API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload PDF file |
| `GET` | `/api/documents` | List all documents |
| `GET` | `/api/documents/{id}` | Get document details + analysis |
| `DELETE` | `/api/documents/{id}` | Delete document and all related data |
| `GET` | `/api/documents/{id}/download` | Download original PDF (presigned URL) |

### Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/{id}/process` | Trigger processing pipeline |
| `GET` | `/api/documents/{id}/status` | Get processing status |
| `GET` | `/api/documents/{id}/analysis` | Get full analysis results |

### Chat (Q&A)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/{id}/chat` | Ask a question about the document |
| `GET` | `/api/documents/{id}/chat/history` | Get chat history |

### Review Queue

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/review/queue` | List documents needing review |
| `PATCH` | `/api/review/{analysis_id}` | Update review status/notes |

---

## 7. Confidence Threshold Management

### Thresholds

```python
class ConfidenceConfig:
    HIGH_THRESHOLD = 0.85      # Auto-accept
    MEDIUM_THRESHOLD = 0.60    # Flag for review
    # Below 0.60 = LOW         # Queue for human review

    # Per-field weights for overall confidence
    WEIGHTS = {
        "classification": 0.25,
        "extraction": 0.30,
        "ocr": 0.20,
        "quality": 0.25,
    }
```

### Routing Logic

```
For each processed document:
  1. Calculate weighted confidence from all pipeline stages
  2. Determine confidence tier (HIGH / MEDIUM / LOW)
  3. Route:
     - HIGH:   status → "completed", auto-accept all extractions
     - MEDIUM: status → "review_needed", flag uncertain fields
     - LOW:    status → "review_needed", requires_review = true
               highlight which pipeline stages had low confidence
```

### Review Dashboard (Streamlit)

- Show documents in review queue sorted by confidence (lowest first)
- Display which fields/stages had low confidence
- Allow human to correct extractions and re-save
- Track review metrics (time to review, correction rate)

---

## 8. LLM Prompts (Anthropic Claude)

### Document Classification Prompt

```
Analyze this document text and classify it into one of these categories:
contract, invoice, report, legal, medical, academic, correspondence, technical, other

Return JSON:
{
  "category": "string",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}
```

### Metadata Extraction Prompt

```
Extract structured metadata from this document:
{
  "title": {"value": "...", "confidence": 0.0-1.0},
  "author": {"value": "...", "confidence": 0.0-1.0},
  "date": {"value": "ISO date or null", "confidence": 0.0-1.0},
  "language": {"value": "ISO 639-1", "confidence": 0.0-1.0},
  "summary": {"value": "2-3 sentence summary", "confidence": 0.0-1.0},
  "key_entities": [{"name": "...", "type": "person|org|location|date|amount", "confidence": 0.0-1.0}],
  "key_terms": ["term1", "term2", ...]
}
```

### Quality Assessment Prompt

```
Assess the quality of this document:
{
  "readability": 0.0-1.0,     // Text clarity and readability
  "completeness": 0.0-1.0,    // Appears complete vs truncated/partial
  "structure": 0.0-1.0,       // Has clear structure (headings, sections)
  "overall": 0.0-1.0,         // Overall quality score
  "issues": ["list of quality issues found"]
}
```

### RAG Q&A System Prompt

```
You are a document analysis assistant. Answer questions based ONLY on the
provided document context. If the answer is not in the context, say so.

Always cite the page number(s) where you found the information.
Provide confidence in your answer (high/medium/low).
```

---

## 9. Frontend (Streamlit)

### Pages

1. **Upload** — Drag-and-drop PDF upload, triggers processing pipeline
2. **Documents** — List of all uploaded documents with status badges
3. **Document Detail** — Full analysis results:
   - Document metadata (title, author, date, category)
   - Classification with confidence badge
   - Extracted entities table
   - Quality assessment scores (visual gauges)
   - Confidence tier indicator (HIGH/MEDIUM/LOW)
   - Page thumbnails
   - Original PDF viewer (iframe or download link)
4. **Chat** — Text area to ask questions about the document
   - Shows retrieved chunks with page references
   - Chat history with sources
5. **Review Queue** — Documents flagged for human review
   - Editable fields for corrections
   - Approve/reject actions

### UI Components

- Confidence badge: green (HIGH), yellow (MEDIUM), red (LOW)
- Processing status indicator with pipeline stage
- Quality score gauges (radial charts)
- Entity highlighting in document text
- Expandable sections for detailed results

---

## 10. Project Structure

```
praxisiq/
├── docs/
│   └── PRD.md
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── documents.py     # Document CRUD endpoints
│   │   │   ├── processing.py    # Processing pipeline endpoints
│   │   │   ├── chat.py          # Q&A endpoints
│   │   │   └── review.py        # Review queue endpoints
│   │   └── dependencies.py      # FastAPI dependencies (DB, MinIO, etc.)
│   ├── pipeline/
│   │   ├── orchestrator.py      # Main pipeline coordinator
│   │   ├── pdf_parser.py        # pypdf text extraction
│   │   ├── ocr_engine.py        # pytesseract OCR with confidence
│   │   ├── classifier.py        # LLM document classification
│   │   ├── extractor.py         # LLM metadata extraction
│   │   ├── quality_assessor.py  # LLM quality scoring
│   │   ├── chunker.py           # Text chunking for embeddings
│   │   ├── embedder.py          # Embedding generation
│   │   └── confidence_router.py # Threshold-based routing logic
│   ├── rag/
│   │   ├── retriever.py         # Vector similarity search
│   │   └── chat.py              # RAG conversation chain
│   ├── storage/
│   │   ├── minio_client.py      # MinIO S3 operations
│   │   └── database.py          # asyncpg connection pool
│   ├── models/
│   │   ├── schemas.py           # Pydantic models (API)
│   │   └── domain.py            # Domain models
│   └── config.py                # Settings (env vars)
├── ui/
│   ├── app.py                   # Streamlit main app
│   ├── pages/
│   │   ├── upload.py
│   │   ├── documents.py
│   │   ├── detail.py
│   │   ├── chat.py
│   │   └── review.py
│   └── components/
│       ├── confidence_badge.py
│       ├── quality_gauge.py
│       └── entity_table.py
├── migrations/
│   └── 001_initial.sql          # Database schema
├── tests/
│   ├── test_pipeline.py
│   ├── test_confidence_router.py
│   └── test_api.py
├── docker-compose.yml           # PostgreSQL + MinIO + App
├── Dockerfile
├── pyproject.toml               # uv project config
├── .env.example
└── README.md
```

---

## 11. Infrastructure (Docker Compose)

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: praxisiq
      POSTGRES_USER: praxisiq
      POSTGRES_PASSWORD: praxisiq_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d

  minio:
    image: minio/minio
    ports: ["9000:9000", "9001:9001"]
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - miniodata:/data

  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres, minio]

  ui:
    build:
      context: .
      dockerfile: Dockerfile.ui
    ports: ["8501:8501"]
    env_file: .env
    depends_on: [api]

volumes:
  pgdata:
  miniodata:
```

---

## 12. Environment Variables

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# PostgreSQL
DATABASE_URL=postgresql://praxisiq:praxisiq_dev@localhost:5432/praxisiq

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=praxisiq
MINIO_USE_SSL=false

# Embeddings (Voyage AI or OpenAI)
EMBEDDING_PROVIDER=voyage          # voyage | openai
VOYAGE_API_KEY=pa-...
EMBEDDING_MODEL=voyage-3
EMBEDDING_DIMENSIONS=1024

# Pipeline
CONFIDENCE_HIGH_THRESHOLD=0.85
CONFIDENCE_MEDIUM_THRESHOLD=0.60
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# API
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 13. Key Skills Demonstrated

| Skill Area | How It's Demonstrated |
|------------|----------------------|
| **IDP (OCR, classification, extraction)** | Full pipeline: PDF parse → OCR fallback → LLM classification → structured extraction |
| **LLM-based document understanding** | Claude for classification, entity extraction, quality assessment, Q&A |
| **Confidence threshold management** | Per-field confidence scores, weighted aggregation, tier-based routing (HIGH/MEDIUM/LOW) |
| **Intelligent routing logic** | Auto-accept vs. flag-for-review vs. human-review queue based on confidence |
| **Python proficiency** | FastAPI async, Pydantic v2, asyncpg, clean architecture |
| **Vector databases & embeddings** | pgvector for semantic search, chunking strategies, embedding generation |
| **Production patterns** | Error handling, processing status tracking, cost estimation, pipeline versioning |
| **AI/ML system architecture** | Modular pipeline stages, pluggable components, observability |

---

## 14. Out of Scope (POC)

- Authentication / authorization
- Multi-tenancy
- Background job queue (BullMQ/Celery) — runs synchronously
- File type support beyond PDF
- Batch processing
- CI/CD pipeline
- Production deployment
- Rate limiting / API security
- Internationalization
- Mobile responsive UI

---

## 15. Success Criteria

1. Upload a PDF and get it stored in MinIO
2. Pipeline processes the PDF through all stages (parse, OCR, classify, extract, quality, chunk, embed)
3. Each stage produces confidence scores
4. Confidence router correctly categorizes documents into HIGH/MEDIUM/LOW tiers
5. Documents with low confidence appear in the review queue
6. User can ask questions about the document and get accurate, sourced answers
7. Vector search returns semantically relevant chunks
8. Processing metadata (tokens used, duration, cost estimate) is tracked
9. Full results are viewable in the Streamlit UI
