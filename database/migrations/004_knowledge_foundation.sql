-- Milestone 4.1 Knowledge Foundation
-- Documents and chunks are plain knowledge preparation records only.
-- This migration intentionally stores document text only.

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('txt', 'markdown', 'pdf')),
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    storage_path TEXT,
    processing_status TEXT NOT NULL DEFAULT 'uploaded'
        CHECK (processing_status IN ('uploaded', 'parsing', 'chunking', 'processed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    name TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'system_placeholder',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_user_status
    ON documents(user_id, processing_status);

CREATE INDEX IF NOT EXISTS idx_documents_user_subject_topic
    ON documents(user_id, subject, topic);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document
    ON document_chunks(document_id, chunk_index);

CREATE INDEX IF NOT EXISTS idx_concepts_user_subject_topic
    ON concepts(user_id, subject, topic);
