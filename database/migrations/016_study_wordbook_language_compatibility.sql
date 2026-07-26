-- Forward-compatible repair for databases where the original Wordbook table
-- was applied before language partitions were introduced.

ALTER TABLE study_word_entries
    ADD COLUMN IF NOT EXISTS language TEXT NOT NULL DEFAULT 'English';

CREATE INDEX IF NOT EXISTS idx_study_word_entries_language_scope
    ON study_word_entries(user_id, goal_id, language, normalized_word);
