-- A Knowledge document can serve several Study Goals while retaining goal_id as its legacy primary link.

CREATE TABLE IF NOT EXISTS document_goal_links (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    goal_id TEXT NOT NULL REFERENCES study_goals(id) ON DELETE CASCADE,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    UNIQUE(user_id, document_id, goal_id)
);

CREATE INDEX IF NOT EXISTS idx_document_goal_links_goal
    ON document_goal_links(user_id, goal_id, document_id);

INSERT INTO document_goal_links (id, user_id, document_id, goal_id, payload, created_at, updated_at)
SELECT
    'legacy-goal-link:' || d.id,
    d.user_id,
    d.id,
    d.goal_id,
    jsonb_build_object(
        'id', 'legacy-goal-link:' || d.id,
        'userId', d.user_id,
        'documentId', d.id,
        'goalId', d.goal_id,
        'createdAt', d.created_at,
        'updatedAt', d.updated_at
    ),
    d.created_at,
    d.updated_at
FROM documents d
WHERE d.planet_type = 'study' AND d.goal_id IS NOT NULL
ON CONFLICT (user_id, document_id, goal_id) DO NOTHING;
