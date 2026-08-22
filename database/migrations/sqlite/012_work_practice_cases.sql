-- Work PracticeCase foundation. Existing Work records remain intact.

ALTER TABLE work_records ADD COLUMN case_id TEXT;

CREATE INDEX IF NOT EXISTS idx_sqlite_work_records_case
    ON work_records(user_id, record_type, case_id, updated_at DESC);
