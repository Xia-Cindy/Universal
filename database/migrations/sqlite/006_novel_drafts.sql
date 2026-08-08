CREATE TABLE IF NOT EXISTS novel_drafts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_novel_drafts_user_updated
    ON novel_drafts(user_id, updated_at DESC);
