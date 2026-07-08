-- Milestone 4.2 Retrieval Foundation
-- Stores embedding metadata/status/reference only.
-- Real vector storage and production vector indexes are intentionally out of scope.

CREATE TABLE IF NOT EXISTS chunk_embeddings (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding_provider TEXT NOT NULL,
    embedding_model TEXT NOT NULL,
    embedding_dimension INTEGER NOT NULL CHECK (embedding_dimension > 0),
    embedding_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (embedding_status IN ('pending', 'embedded', 'failed')),
    embedding_ref TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, chunk_id)
);

CREATE INDEX IF NOT EXISTS idx_chunk_embeddings_document_status
    ON chunk_embeddings(user_id, document_id, embedding_status);
