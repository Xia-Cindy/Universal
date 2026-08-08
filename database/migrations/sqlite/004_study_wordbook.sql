-- Study Planet Wordbook: learner-owned vocabulary records and notes.

CREATE TABLE IF NOT EXISTS study_word_entries (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    goal_id TEXT,
    normalized_word TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'English',
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_study_word_entries_scope
    ON study_word_entries(user_id, goal_id, language, normalized_word);
