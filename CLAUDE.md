# IDP-POC (PraxisIQ) - Intelligent Document Processing Pipeline

> 10-stage AI document processing pipeline for classifying, extracting, and validating data from PDFs.

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, Pydantic v2
- **Database:** PostgreSQL 16 + pgvector, raw asyncpg (no ORM), single SQL migration (`migrations/001_initial.sql`)
- **Storage:** MinIO (S3-compatible)
- **AI/ML:** Anthropic Claude (classification, extraction, quality), Voyage AI embeddings (hash-based fallback if `VOYAGE_API_KEY` unset), PyTesseract + pdf2image (OCR), pypdf
- **UI:** Streamlit (data exploration dashboard)
- **Runtime:** Docker, uv (package manager)

## Commands

```bash
# Setup
cp .env.example .env
uv sync                                          # Install dependencies
docker compose up -d                             # Start PG (pgvector) + MinIO
# migrations/001_initial.sql is applied automatically by the Postgres
# container's docker-entrypoint-initdb.d — no separate migration command

# Development
uv run uvicorn src.api.main:app --reload --port 8000

# Testing
uv run pytest                        # All tests
uv run pytest -m "not slow"          # Quick tests only

# Streamlit UI
uv run streamlit run ui/app.py --server.port 8501

# Docker (full stack)
docker compose up --build
```

## Architecture

```
src/
├── api/
│   ├── main.py           # FastAPI app entry point
│   └── routes/           # documents, processing, chat, review
├── pipeline/
│   ├── orchestrator.py   # 10-stage pipeline coordinator
│   └── ...                # pdf_parser, ocr_engine, classifier, extractor,
│                          # quality_assessor, confidence_router, chunker, embedder
├── rag/                  # retriever.py (pgvector similarity search), chat.py
├── storage/               # database.py (asyncpg pool), minio_client.py
├── models/
│   └── schemas.py         # Pydantic request/response + domain models (no SQLAlchemy)
└── config.py              # Settings via pydantic-settings

ui/                        # Streamlit dashboard (top-level, not src/ui/)
├── app.py
├── pages/                 # documents, review, upload
└── components/

migrations/                # Raw SQL (001_initial.sql) — no Alembic
sample-pdfs/                # Test PDF documents
tests/                      # pytest test suite
```

## Pipeline Stages

Source of truth: `src/pipeline/orchestrator.py`.

1. **PDF Parsing** (pypdf) — raw text per page, page count
2. **OCR** (pytesseract + pdf2image, 300 DPI) — only for pages without extractable text
3. **Content Merge** — best text source per page
4. **Classification** (Claude) — category + confidence
5. **Metadata Extraction** (Claude) — title, author, date, language, entities, key terms, summary
6. **Quality Assessment** (Claude) — readability, completeness, structure scores
7. **Confidence Routing** — weighted aggregation → HIGH/MEDIUM/LOW tier, review flag
8. **Chunking** — sliding window (512 tokens, 50 overlap)
9. **Embeddings** — Voyage AI (voyage-3) if `VOYAGE_API_KEY` is set, otherwise a deterministic SHA-256 hash fallback (no semantic similarity)
10. **Store Results** — PostgreSQL + pgvector

## Environment Variables

```env
DATABASE_URL=postgresql://praxisiq:praxisiq_dev@localhost:5433/praxisiq
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...        # optional — hash-based embedding fallback if unset
```

## Recommended Agents

`python-agent`, `ai-engineer`, `computer-vision-engineer`, `fastapi-expert`, `data-engineer`
