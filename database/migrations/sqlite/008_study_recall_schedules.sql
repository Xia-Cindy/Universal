-- F3: user-controlled spaced recall for existing Knowledge cards and Wordbook entries.

CREATE TABLE IF NOT EXISTS study_recall_schedules (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    goal_id TEXT,
    next_review_date TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, source_type, source_id)
);

CREATE INDEX IF NOT EXISTS idx_sqlite_study_recall_schedules_queue
    ON study_recall_schedules(user_id, next_review_date);

CREATE INDEX IF NOT EXISTS idx_sqlite_study_recall_schedules_goal
    ON study_recall_schedules(user_id, goal_id, next_review_date);
