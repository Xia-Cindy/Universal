-- F3: user-controlled spaced recall for existing Knowledge cards and Wordbook entries.

CREATE TABLE IF NOT EXISTS study_recall_schedules (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL CHECK (source_type IN ('knowledge_annotation', 'wordbook_entry')),
    source_id TEXT NOT NULL,
    goal_id TEXT REFERENCES study_goals(id) ON DELETE SET NULL,
    next_review_date DATE NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    UNIQUE(user_id, source_type, source_id)
);

CREATE INDEX IF NOT EXISTS idx_study_recall_schedules_queue
    ON study_recall_schedules(user_id, next_review_date);

CREATE INDEX IF NOT EXISTS idx_study_recall_schedules_goal
    ON study_recall_schedules(user_id, goal_id, next_review_date);
