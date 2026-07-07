-- Milestone 3 AI Core + Study Tutor foundation.
-- No vector, embedding, document chunk, RAG, or Knowledge Graph tables.

CREATE TABLE IF NOT EXISTS learning_events (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_learning_events_user_created
    ON learning_events (user_id, created_at DESC);

