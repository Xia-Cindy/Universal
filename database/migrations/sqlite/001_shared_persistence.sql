CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_planet_context (
    user_id TEXT NOT NULL,
    planet_type TEXT NOT NULL,
    current_goal_id TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, planet_type)
);

CREATE TABLE IF NOT EXISTS study_goals (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    goal_name TEXT NOT NULL,
    goal_type TEXT NOT NULL,
    exam_name TEXT,
    deadline TEXT,
    description TEXT NOT NULL,
    subjects TEXT NOT NULL,
    current_level TEXT NOT NULL,
    daily_available_minutes INTEGER NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_goals_user_updated
    ON study_goals(user_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS study_plans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    goal_id TEXT NOT NULL,
    plan_type TEXT NOT NULL,
    parent_id TEXT,
    year INTEGER,
    month INTEGER,
    week_start TEXT,
    week_end TEXT,
    title TEXT NOT NULL,
    focus TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_plans_goal_type
    ON study_plans(user_id, goal_id, plan_type, created_at);

CREATE TABLE IF NOT EXISTS daily_tasks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    goal_id TEXT NOT NULL,
    week_plan_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    task_date TEXT NOT NULL,
    estimated_minutes INTEGER NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_tasks_goal_date
    ON daily_tasks(user_id, goal_id, task_date);

CREATE TABLE IF NOT EXISTS study_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    task_id TEXT,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_minutes INTEGER NOT NULL,
    notes TEXT NOT NULL,
    feeling TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_sessions_user_start
    ON study_sessions(user_id, start_time);

CREATE TABLE IF NOT EXISTS learning_events (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    goal_id TEXT,
    planet_type TEXT NOT NULL,
    tech_stack_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_documents_user_scope
    ON documents(user_id, planet_type, goal_id, tech_stack_id);

CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_entries (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    planet_type TEXT,
    session_id TEXT,
    status TEXT NOT NULL,
    importance INTEGER NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_accessed_at TEXT,
    expires_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_sqlite_memory_scope
    ON memory_entries(user_id, scope, status, planet_type, session_id);

CREATE TABLE IF NOT EXISTS work_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    record_type TEXT NOT NULL,
    tech_stack_id TEXT,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_work_records_type
    ON work_records(user_id, record_type, tech_stack_id, updated_at);

CREATE TABLE IF NOT EXISTS work_evidence (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    tech_stack_id TEXT,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_work_evidence_user
    ON work_evidence(user_id, tech_stack_id, source_type, source_id);
