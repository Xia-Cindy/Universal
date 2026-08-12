-- Optional user/document reading positions. This never stores document content or Goal mastery.

CREATE TABLE IF NOT EXISTS reading_progress (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    spread_index INTEGER NOT NULL DEFAULT 0,
    page_number INTEGER NOT NULL DEFAULT 1,
    bookmark_label TEXT,
    client_updated_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    UNIQUE(user_id, document_id)
);

CREATE INDEX IF NOT EXISTS idx_reading_progress_user_updated
    ON reading_progress(user_id, updated_at DESC);
