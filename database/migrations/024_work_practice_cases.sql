-- Work PracticeCase foundation.
-- Existing Work records remain intact. case_id establishes the shared
-- relation column later Artifacts, Backlog Items and Labs can reuse.

ALTER TABLE work_records
    ADD COLUMN IF NOT EXISTS case_id TEXT;

CREATE INDEX IF NOT EXISTS idx_work_records_case
    ON work_records(user_id, record_type, case_id, updated_at DESC);
