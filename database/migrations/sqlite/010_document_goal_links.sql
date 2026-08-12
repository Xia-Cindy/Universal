-- SQLite counterpart; records the legacy documents.goal_id as the initial primary link.

CREATE TABLE IF NOT EXISTS document_goal_links (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    goal_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, document_id, goal_id)
);

CREATE INDEX IF NOT EXISTS idx_sqlite_document_goal_links_goal
    ON document_goal_links(user_id, goal_id, document_id);

INSERT OR IGNORE INTO document_goal_links (id, user_id, document_id, goal_id, payload, created_at, updated_at)
SELECT
    'legacy-goal-link:' || id,
    user_id,
    id,
    goal_id,
    '{"id":"legacy-goal-link:' || id || '","userId":"' || user_id || '","documentId":"' || id || '","goalId":"' || goal_id || '","createdAt":"' || created_at || '","updatedAt":"' || updated_at || '"}',
    created_at,
    updated_at
FROM documents
WHERE planet_type = 'study' AND goal_id IS NOT NULL;
