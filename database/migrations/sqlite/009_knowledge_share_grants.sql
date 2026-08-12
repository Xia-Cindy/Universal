-- SQLite development/test counterpart for revocable Knowledge-to-Work grants.

CREATE TABLE IF NOT EXISTS knowledge_share_grants (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    source_goal_id TEXT NOT NULL,
    tech_stack_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, document_id, tech_stack_id)
);

CREATE INDEX IF NOT EXISTS idx_sqlite_knowledge_share_grants_work_scope
    ON knowledge_share_grants(user_id, tech_stack_id, created_at);

CREATE INDEX IF NOT EXISTS idx_sqlite_knowledge_share_grants_document
    ON knowledge_share_grants(user_id, document_id);
