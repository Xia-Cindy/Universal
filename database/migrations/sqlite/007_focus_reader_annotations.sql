-- Focus Reader: learner-owned notes and recall cards anchored to Knowledge passages.

CREATE TABLE IF NOT EXISTS knowledge_annotations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    goal_id TEXT,
    annotation_type TEXT NOT NULL,
    mastered INTEGER NOT NULL DEFAULT 0,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sqlite_knowledge_annotations_document
    ON knowledge_annotations(user_id, document_id, created_at);

CREATE INDEX IF NOT EXISTS idx_sqlite_knowledge_annotations_goal_mastered
    ON knowledge_annotations(user_id, goal_id, mastered);
