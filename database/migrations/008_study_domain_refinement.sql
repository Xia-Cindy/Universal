-- Milestone 7.5 Study Domain Model Refinement.
-- Adds plan hierarchy metadata and optional goal linkage for Knowledge documents.

ALTER TABLE year_plans
    ADD COLUMN IF NOT EXISTS plan_type TEXT NOT NULL DEFAULT 'long_term'
    CHECK (plan_type IN ('long_term', 'monthly', 'weekly', 'daily'));

ALTER TABLE month_plans
    ADD COLUMN IF NOT EXISTS plan_type TEXT NOT NULL DEFAULT 'monthly'
    CHECK (plan_type IN ('long_term', 'monthly', 'weekly', 'daily'));

ALTER TABLE week_plans
    ADD COLUMN IF NOT EXISTS plan_type TEXT NOT NULL DEFAULT 'weekly'
    CHECK (plan_type IN ('long_term', 'monthly', 'weekly', 'daily'));

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS goal_id TEXT NULL REFERENCES study_goals(id) ON DELETE SET NULL;

DROP INDEX IF EXISTS idx_study_goals_one_active_per_user;

CREATE INDEX IF NOT EXISTS idx_documents_user_goal
    ON documents(user_id, goal_id);
