-- Expand Study Goal beyond exam-only learning scenarios.
-- Existing rows are preserved and treated as exam goals.

ALTER TABLE study_goals
    ADD COLUMN IF NOT EXISTS goal_type TEXT NOT NULL DEFAULT 'exam'
    CHECK (goal_type IN ('exam', 'learning', 'reading', 'growth'));

ALTER TABLE study_goals
    ADD COLUMN IF NOT EXISTS description TEXT NOT NULL DEFAULT '';

ALTER TABLE study_goals
    ALTER COLUMN deadline DROP NOT NULL;

ALTER TABLE study_goals
    ALTER COLUMN exam_name DROP NOT NULL;

CREATE INDEX IF NOT EXISTS idx_study_goals_user_type_status
    ON study_goals (user_id, goal_type, status);
