-- Knowledge Space Metadata
-- Extends shared Knowledge documents with Planet and Work Tech Stack binding.
-- Existing documents remain valid and default to Study scope.

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS planet_type TEXT NOT NULL DEFAULT 'study';

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS tech_stack_id TEXT;

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS tags JSONB NOT NULL DEFAULT '[]'::JSONB;

CREATE INDEX IF NOT EXISTS idx_documents_planet_scope
    ON documents(user_id, planet_type);

CREATE INDEX IF NOT EXISTS idx_documents_work_tech_stack
    ON documents(user_id, tech_stack_id);

CREATE INDEX IF NOT EXISTS idx_documents_tags_gin
    ON documents USING GIN(tags);
