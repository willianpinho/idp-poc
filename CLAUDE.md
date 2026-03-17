# IDP-POC - Intelligent Document Processing Pipeline

> 10-stage AI document processing pipeline for classifying, extracting, and validating data from PDFs.

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, Pydantic
- **Database:** PostgreSQL (asyncpg), Alembic migrations
- **Storage:** MinIO (S3-compatible)
- **OCR/ML:** PyTesseract, pdf2image, Anthropic SDK, Pillow
- **UI:** Streamlit (data exploration dashboard)
- **Runtime:** Docker, uv (package manager)

## Commands

```bash
# Setup
cp .env.example .env
uv sync                              # Install dependencies
docker compose up -d                 # Start PG + MinIO
alembic upgrade head                 # Run migrations

# Development
uv run uvicorn src.main:app --reload --port 8000

# Testing
uv run pytest                        # All tests
uv run pytest -m "not slow"          # Quick tests only

# Streamlit UI
uv run streamlit run src/ui/app.py

# Docker (full stack)
docker compose up --build
```

## Architecture

```
src/
├── main.py              # FastAPI app entry point
├── config.py            # Settings (Pydantic BaseSettings)
├── db.py                # AsyncPG connection pool
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic (processing pipeline)
├── api/                 # FastAPI routes
└── ui/                  # Streamlit dashboard

migrations/              # Alembic migration scripts
sample-pdfs/             # Test PDF documents
tests/                   # pytest test suite
```

## Pipeline Stages

1. Upload → 2. OCR → 3. Classification → 4. Extraction → 5. Validation → 6. Enrichment → 7. Storage → 8. Indexing → 9. Review → 10. Export

## Environment Variables

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/idp_dev
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
ANTHROPIC_API_KEY=sk-ant-...
```

## Recommended Agents

`python-agent`, `ai-engineer`, `computer-vision-engineer`, `fastapi-expert`, `data-engineer`
