-- SQLite counterpart for optional user/document reading positions.

CREATE TABLE IF NOT EXISTS reading_progress (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    spread_index INTEGER NOT NULL DEFAULT 0,
    page_number INTEGER NOT NULL DEFAULT 1,
    bookmark_label TEXT,
    client_updated_at TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, document_id)
);

CREATE INDEX IF NOT EXISTS idx_sqlite_reading_progress_user_updated
    ON reading_progress(user_id, updated_at DESC);
