-- Work Content Records
-- Adds Tech Stack-owned articles and learning records.

CREATE TABLE IF NOT EXISTS work_articles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tech_stack_id TEXT NOT NULL REFERENCES tech_stacks(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    article_type TEXT NOT NULL DEFAULT 'knowledge',
    summary TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS work_learning_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tech_stack_id TEXT NOT NULL REFERENCES tech_stacks(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    minutes INTEGER NOT NULL DEFAULT 0,
    tags TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'recorded',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_work_articles_stack_status
    ON work_articles(user_id, tech_stack_id, status);

CREATE INDEX IF NOT EXISTS idx_work_learning_records_stack
    ON work_learning_records(user_id, tech_stack_id);
