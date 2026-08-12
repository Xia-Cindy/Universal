-- Revocable Study Knowledge references for explicit Work Tech Stack use.

CREATE TABLE IF NOT EXISTS knowledge_share_grants (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_goal_id TEXT NOT NULL REFERENCES study_goals(id) ON DELETE CASCADE,
    tech_stack_id TEXT NOT NULL REFERENCES tech_stacks(id) ON DELETE CASCADE,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    UNIQUE(user_id, document_id, tech_stack_id)
);

CREATE INDEX IF NOT EXISTS idx_knowledge_share_grants_work_scope
    ON knowledge_share_grants(user_id, tech_stack_id, created_at);

CREATE INDEX IF NOT EXISTS idx_knowledge_share_grants_document
    ON knowledge_share_grants(user_id, document_id);
