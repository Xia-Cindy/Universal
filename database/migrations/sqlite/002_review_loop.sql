CREATE TABLE IF NOT EXISTS wrong_questions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    goal_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_wrong_questions_user_goal
    ON wrong_questions(user_id, goal_id, created_at DESC);

CREATE TABLE IF NOT EXISTS review_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    wrong_question_id TEXT NOT NULL,
    due_date TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_review_items_user_due
    ON review_items(user_id, due_date);
