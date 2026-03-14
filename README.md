<p align="center">
  <h1 align="center">IDP &mdash; Intelligent Document Processing</h1>
  <p align="center">
    A 10-stage AI pipeline that transforms raw PDFs into structured, searchable knowledge<br/>
    with confidence-scored routing, RAG-powered Q&A, and human-in-the-loop review.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-16_%2B_pgvector-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Claude-Sonnet_4-D97757?logo=anthropic&logoColor=white" alt="Claude" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License" />
</p>

---

## Architecture

```
                                    IDP Pipeline
 PDF Upload                                                         Results
 =========                                                         =======

              +----------------------------------------------------+
              |                                                    |
  .---.       |  1. Parse    2. OCR     3. Merge    4. Classify    |     .-----------.
 | PDF | ---->|  (pypdf)  (tesseract) (best src)    (Claude)       |---->| PostgreSQL |
  '---'       |                                                    |     |  pgvector  |
              |  5. Extract  6. Quality  7. Route   8. Chunk       |     '-----------'
              |  (Claude)    (Claude)   (scoring)  (sliding)       |          |
              |                                                    |          v
              |  9. Embed   10. Store                              |    .-----------.
              | (Voyage AI) (pgvector)                             |    | RAG Chat  |
              |                                                    |    | Q&A       |
              +----------------------------------------------------+    '-----------'

                         Confidence Routing (Stage 7)
              +----------------------------------------------------+
              |                                                    |
              |   HIGH (>= 0.85)  --> Auto-accept                  |
              |   MEDIUM (0.60-0.85) --> Flag for review            |
              |   LOW (< 0.60)   --> Require human review          |
              |                                                    |
              +----------------------------------------------------+
```

## Key Features

**10-Stage AI Pipeline** -- Each document passes through parsing, OCR, classification, metadata extraction, quality assessment, confidence routing, chunking, and vector embedding. Every stage produces traceable scores.

**Confidence-Based Routing** -- A weighted aggregation of classification, extraction, OCR, and quality scores determines whether a document is auto-accepted, flagged for review, or held for human intervention.

**RAG-Powered Chat** -- Ask questions about any processed document. The system retrieves relevant chunks via pgvector similarity search and generates grounded answers with source citations.

**Human Review Queue** -- Documents below the confidence threshold surface in a review queue sorted by urgency. Reviewers can approve, annotate, or reject with notes.

**Streamlit Dashboard** -- Three-page UI for uploading documents, exploring analysis results (quality metrics, entities, key terms), and managing the review queue.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Tesseract OCR (`brew install tesseract` on macOS)
- Poppler (`brew install poppler` on macOS, needed by pdf2image)

### 1. Clone and configure

```bash
git clone https://github.com/willianpinho/idp-poc.git
cd idp-poc
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY and VOYAGE_API_KEY
```

### 2. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL (with pgvector) on port **5433** and MinIO on ports **9000/9001**.

### 3. Install dependencies

```bash
uv sync                    # or: pip install -e ".[ui,dev]"
```

### 4. Run the API

```bash
uv run uvicorn src.api.main:app --reload --port 8000
```

### 5. Run the Streamlit UI (optional)

```bash
uv run streamlit run ui/app.py --server.port 8501
```

### 6. Upload a document

```bash
curl -X POST http://localhost:8000/api/documents \
  -F "file=@sample-pdfs/contract.pdf"
```

Then trigger processing:

```bash
curl -X POST http://localhost:8000/api/documents/{id}/process
```

## Pipeline Stages

| Stage | Name | Technology | Output |
|-------|------|-----------|--------|
| 1 | **PDF Parsing** | pypdf | Raw text per page, page count |
| 2 | **OCR** | pytesseract + pdf2image (300 DPI) | Text for image-only pages |
| 3 | **Content Merge** | Custom | Best text source per page |
| 4 | **Classification** | Claude Sonnet 4 | Category + confidence (contract, invoice, report, legal, medical, academic, ...) |
| 5 | **Metadata Extraction** | Claude Sonnet 4 | Title, author, date, language, entities, key terms, summary |
| 6 | **Quality Assessment** | Claude Sonnet 4 | Readability, completeness, and structure scores |
| 7 | **Confidence Routing** | Weighted aggregation | Tier (HIGH/MEDIUM/LOW), review flag |
| 8 | **Text Chunking** | Sliding window | 512-token chunks with 50-token overlap |
| 9 | **Embeddings** | Voyage AI (voyage-3) | 1024-dim vectors (hash fallback) |
| 10 | **Store Results** | PostgreSQL + pgvector | Persistent analysis + vector index |

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents` | Upload a PDF document |
| `GET` | `/api/documents` | List all documents with status |
| `POST` | `/api/documents/{id}/process` | Trigger the 10-stage pipeline |
| `GET` | `/api/documents/{id}/analysis` | Retrieve full analysis results |
| `POST` | `/api/documents/{id}/chat` | RAG-powered Q&A over document |
| `GET` | `/api/review/queue` | List documents pending human review |
| `PATCH` | `/api/review/{id}` | Update review status and notes |
| `GET` | `/health` | Health check |

Interactive API docs available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | -- | **Required.** Anthropic API key for Claude |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Claude model identifier |
| `VOYAGE_API_KEY` | -- | **Required.** Voyage AI API key for embeddings |
| `DATABASE_URL` | `postgresql://idp-app:idp-app_dev@localhost:5433/idp-app` | PostgreSQL connection string |
| `MINIO_ENDPOINT` | `localhost:9000` | MinIO S3-compatible endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `MINIO_BUCKET` | `idp-app` | MinIO bucket name |
| `MINIO_USE_SSL` | `false` | Enable SSL for MinIO |
| `EMBEDDING_PROVIDER` | `voyage` | Embedding provider |
| `EMBEDDING_MODEL` | `voyage-3` | Embedding model name |
| `EMBEDDING_DIMENSIONS` | `1024` | Embedding vector dimensions |
| `CONFIDENCE_HIGH_THRESHOLD` | `0.85` | Auto-accept threshold |
| `CONFIDENCE_MEDIUM_THRESHOLD` | `0.60` | Review threshold |
| `CHUNK_SIZE` | `512` | Tokens per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `API_HOST` | `0.0.0.0` | API bind address |
| `API_PORT` | `8000` | API port |

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API** | FastAPI, Pydantic v2, uvicorn | Async REST API with validation |
| **AI/LLM** | Anthropic Claude Sonnet 4 | Classification, extraction, quality assessment, chat |
| **Embeddings** | Voyage AI (voyage-3, 1024d) | Semantic vector embeddings for RAG |
| **OCR** | Tesseract + pdf2image | Text extraction from scanned/image PDFs |
| **PDF** | pypdf | Native PDF text extraction |
| **Database** | PostgreSQL 16 + pgvector | Relational storage + vector similarity search |
| **Object Storage** | MinIO (S3-compatible) | PDF file storage |
| **UI** | Streamlit + Plotly | Interactive dashboard |
| **Containers** | Docker Compose | Infrastructure orchestration |
| **Package Mgmt** | uv + hatchling | Fast dependency resolution and builds |
| **Linting** | Ruff | Code formatting and linting |
| **Testing** | pytest + pytest-asyncio | Async test suite |

## Project Structure

```
idp-poc/
├── src/
│   ├── api/
│   │   ├── main.py                  # FastAPI app entry point
│   │   └── routes/
│   │       ├── documents.py         # Upload, list, get analysis
│   │       ├── processing.py        # Trigger pipeline
│   │       ├── chat.py              # RAG-powered Q&A
│   │       └── review.py            # Human review queue
│   ├── pipeline/
│   │   ├── orchestrator.py          # 10-stage pipeline coordinator
│   │   ├── pdf_parser.py            # Stage 1: PDF text extraction
│   │   ├── ocr_engine.py            # Stage 2: OCR with Tesseract
│   │   ├── classifier.py            # Stage 4: Document classification
│   │   ├── extractor.py             # Stage 5: Metadata extraction
│   │   ├── quality_assessor.py      # Stage 6: Quality scoring
│   │   ├── confidence_router.py     # Stage 7: Confidence routing
│   │   ├── chunker.py               # Stage 8: Text chunking
│   │   ├── embedder.py              # Stage 9: Vector embeddings
│   │   └── llm_utils.py             # Shared LLM utilities
│   ├── rag/
│   │   ├── retriever.py             # Vector similarity search
│   │   └── chat.py                  # Conversational RAG
│   ├── storage/
│   │   ├── database.py              # PostgreSQL connection pool
│   │   └── minio_client.py          # MinIO file operations
│   ├── models/
│   │   └── schemas.py               # Pydantic models
│   └── config.py                    # Settings via pydantic-settings
├── ui/
│   ├── app.py                       # Streamlit entry point
│   └── views/
│       ├── upload.py                # Upload page
│       ├── documents.py             # Document analysis page
│       └── review.py                # Review queue page
├── migrations/
│   └── 001_initial.sql              # Database schema (pgvector)
├── sample-pdfs/
│   └── generate_samples.py          # Sample PDF generator
├── tests/                           # Test suite
├── docker-compose.yml               # PostgreSQL + MinIO
├── Dockerfile                       # API container
├── Dockerfile.ui                    # Streamlit container
├── pyproject.toml                   # Project config (uv/hatch)
└── .env.example                     # Environment template
```

## Database Schema

Four tables with pgvector support:

- **documents** -- Uploaded file metadata and processing status
- **document_analysis** -- Full analysis results (classification, extraction, quality, confidence, OCR details, processing metrics)
- **document_chunks** -- Text chunks with 1024-dim vector embeddings for RAG retrieval
- **chat_messages** -- Conversation history per document with source references

## Screenshots

> Screenshots coming soon. The Streamlit UI includes three pages: Upload, Document Analysis, and Review Queue.

<!-- Uncomment and update paths when screenshots are available:
![Upload Page](docs/screenshots/upload.png)
![Analysis Page](docs/screenshots/analysis.png)
![Review Queue](docs/screenshots/review.png)
-->

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Lint and format
uv run ruff check src/ --fix
uv run ruff format src/

# Generate sample PDFs for testing
uv run python sample-pdfs/generate_samples.py
```

## License

[MIT](LICENSE) -- Willian Pinho, 2026
