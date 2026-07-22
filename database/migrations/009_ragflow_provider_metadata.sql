-- Milestone 8.1 RAGFlow Provider Adapter
-- Adds provider references while preserving local Knowledge compatibility.

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS provider TEXT NOT NULL DEFAULT 'local';

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS content_encoding TEXT NOT NULL DEFAULT 'text';

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS provider_dataset_id TEXT;

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS provider_document_id TEXT;

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS provider_status TEXT;

CREATE INDEX IF NOT EXISTS idx_documents_provider_refs
    ON documents(user_id, provider, provider_dataset_id, provider_document_id);
