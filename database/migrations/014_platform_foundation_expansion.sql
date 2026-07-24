-- Platform persistence expansion.
-- These compatibility columns let the PostgreSQL adapters reuse the existing
-- repository contracts while preserving the original normalized tables.

CREATE TABLE IF NOT EXISTS user_planet_context (
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    planet_type TEXT NOT NULL,
    current_goal_id TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, planet_type)
);

CREATE TABLE IF NOT EXISTS study_plans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    goal_id TEXT NOT NULL REFERENCES study_goals(id),
    plan_type TEXT NOT NULL,
    parent_id TEXT,
    year INTEGER,
    month INTEGER,
    week_start DATE,
    week_end DATE,
    title TEXT NOT NULL,
    focus TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

ALTER TABLE daily_tasks
    ADD COLUMN IF NOT EXISTS priority TEXT NOT NULL DEFAULT 'medium',
    ADD COLUMN IF NOT EXISTS sort_order INTEGER NOT NULL DEFAULT 0;

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    ADD COLUMN IF NOT EXISTS content TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS content_encoding TEXT NOT NULL DEFAULT 'text',
    ADD COLUMN IF NOT EXISTS planet_type TEXT NOT NULL DEFAULT 'study',
    ADD COLUMN IF NOT EXISTS tech_stack_id TEXT,
    ADD COLUMN IF NOT EXISTS tags JSONB NOT NULL DEFAULT '[]'::JSONB,
    ADD COLUMN IF NOT EXISTS provider TEXT NOT NULL DEFAULT 'local',
    ADD COLUMN IF NOT EXISTS provider_dataset_id TEXT,
    ADD COLUMN IF NOT EXISTS provider_document_id TEXT,
    ADD COLUMN IF NOT EXISTS provider_status TEXT;

ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS payload JSONB NOT NULL DEFAULT '{}'::JSONB;

ALTER TABLE concepts
    ADD COLUMN IF NOT EXISTS payload JSONB NOT NULL DEFAULT '{}'::JSONB;

ALTER TABLE memory_entries
    ADD COLUMN IF NOT EXISTS payload JSONB NOT NULL DEFAULT '{}'::JSONB;

CREATE TABLE IF NOT EXISTS work_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    record_type TEXT NOT NULL,
    tech_stack_id TEXT,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS wrong_questions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    goal_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS review_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    wrong_question_id TEXT NOT NULL,
    due_date DATE NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_accounts (
    user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_verification_codes (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_token ON auth_sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_verification_codes_email ON email_verification_codes(email, created_at DESC);
