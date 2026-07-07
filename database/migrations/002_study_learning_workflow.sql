-- Milestone 2 Study Planet learning workflow schema.
-- This layer covers Goal, Plan, Daily Task and Study Session only.

CREATE TABLE IF NOT EXISTS study_goals (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_name TEXT NOT NULL,
    exam_name TEXT NOT NULL,
    deadline DATE NOT NULL,
    subjects JSONB NOT NULL,
    current_level TEXT NOT NULL,
    daily_available_minutes INTEGER NOT NULL CHECK (daily_available_minutes > 0),
    priority TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL CHECK (status IN ('active', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_study_goals_one_active_per_user
    ON study_goals (user_id)
    WHERE status = 'active';

CREATE TABLE IF NOT EXISTS year_plans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_id TEXT NOT NULL REFERENCES study_goals(id),
    year INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'draft', 'completed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_year_plans_user_goal_status
    ON year_plans (user_id, goal_id, status);

CREATE TABLE IF NOT EXISTS month_plans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_id TEXT NOT NULL REFERENCES study_goals(id),
    year_plan_id TEXT NOT NULL REFERENCES year_plans(id),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    title TEXT NOT NULL,
    focus TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'draft', 'completed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS week_plans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_id TEXT NOT NULL REFERENCES study_goals(id),
    month_plan_id TEXT NOT NULL REFERENCES month_plans(id),
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    title TEXT NOT NULL,
    focus TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'draft', 'completed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (week_end >= week_start)
);

CREATE TABLE IF NOT EXISTS daily_tasks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_id TEXT NOT NULL REFERENCES study_goals(id),
    week_plan_id TEXT NOT NULL REFERENCES week_plans(id),
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    task_date DATE NOT NULL,
    estimated_minutes INTEGER NOT NULL CHECK (estimated_minutes > 0),
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed')),
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_daily_tasks_goal_date
    ON daily_tasks (goal_id, task_date);

CREATE INDEX IF NOT EXISTS idx_daily_tasks_goal_status
    ON daily_tasks (goal_id, status);

CREATE TABLE IF NOT EXISTS study_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    task_id TEXT NULL REFERENCES daily_tasks(id),
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 0 CHECK (duration_minutes >= 0),
    notes TEXT NOT NULL DEFAULT '',
    feeling TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'finished')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        (status = 'in_progress' AND end_time IS NULL AND duration_minutes = 0)
        OR (status = 'finished' AND end_time IS NOT NULL AND duration_minutes > 0)
    )
);

CREATE INDEX IF NOT EXISTS idx_study_sessions_user_start_time
    ON study_sessions (user_id, start_time);

CREATE INDEX IF NOT EXISTS idx_study_sessions_task_status
    ON study_sessions (task_id, status);

