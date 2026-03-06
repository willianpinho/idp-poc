CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL DEFAULT 'application/pdf',
    file_size_bytes BIGINT NOT NULL,
    page_count INTEGER,
    storage_key VARCHAR(1000) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Processing results
CREATE TABLE document_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    category VARCHAR(100),
    category_confidence FLOAT,
    title VARCHAR(1000),
    author VARCHAR(500),
    document_date VARCHAR(200),
    language VARCHAR(50),
    summary TEXT,
    key_entities JSONB DEFAULT '[]',
    key_terms JSONB DEFAULT '[]',
    extracted_metadata JSONB DEFAULT '{}',
    quality_score FLOAT,
    readability_score FLOAT,
    completeness_score FLOAT,
    structure_score FLOAT,
    quality_details JSONB DEFAULT '{}',
    overall_confidence FLOAT,
    confidence_tier VARCHAR(20),
    requires_review BOOLEAN DEFAULT FALSE,
    review_notes TEXT,
    ocr_applied BOOLEAN DEFAULT FALSE,
    ocr_confidence FLOAT,
    ocr_engine VARCHAR(50),
    pages_ocr_applied INTEGER[],
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
    page_numbers INTEGER[],
    token_count INTEGER,
    embedding vector(1024),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chat history for Q&A
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_analysis_document ON document_analysis(document_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_analysis_confidence ON document_analysis(confidence_tier);
CREATE INDEX idx_chat_document ON chat_messages(document_id);
