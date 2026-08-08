-- Study Planet Wordbook: learner-owned vocabulary records and notes.

CREATE TABLE IF NOT EXISTS study_word_entries (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_id TEXT REFERENCES study_goals(id) ON DELETE SET NULL,
    normalized_word TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'English',
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_study_word_entries_scope
    ON study_word_entries(user_id, goal_id, language, normalized_word);
