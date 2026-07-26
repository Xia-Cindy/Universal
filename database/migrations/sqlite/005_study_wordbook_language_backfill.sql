-- Compatibility migration for databases created when 004 lacked `language`.
-- SQLitePersistence adds the column conditionally before this index is applied.

CREATE INDEX IF NOT EXISTS idx_sqlite_study_word_entries_language_scope
    ON study_word_entries(user_id, goal_id, language, normalized_word);
