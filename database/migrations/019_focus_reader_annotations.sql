-- Focus Reader: learner-owned notes and recall cards anchored to Knowledge passages.

CREATE TABLE IF NOT EXISTS knowledge_annotations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    goal_id TEXT REFERENCES study_goals(id) ON DELETE SET NULL,
    annotation_type TEXT NOT NULL CHECK (annotation_type IN ('note', 'card')),
    mastered BOOLEAN NOT NULL DEFAULT FALSE,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_knowledge_annotations_document
    ON knowledge_annotations(user_id, document_id, created_at);

CREATE INDEX IF NOT EXISTS idx_knowledge_annotations_goal_mastered
    ON knowledge_annotations(user_id, goal_id, mastered);
