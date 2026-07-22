-- Milestone 7.9 Study Plan Calendar
-- Adds user-facing Daily Task priority while preserving existing tasks.

ALTER TABLE daily_tasks
    ADD COLUMN IF NOT EXISTS priority TEXT NOT NULL DEFAULT 'medium';

CREATE INDEX IF NOT EXISTS idx_daily_tasks_goal_date_priority
    ON daily_tasks(user_id, goal_id, task_date, priority);
