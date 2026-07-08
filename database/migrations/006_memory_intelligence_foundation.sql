-- Milestone 5 Memory Intelligence Foundation
-- Memory remains user-owned and scoped. This migration adds lifecycle and
-- retrieval preparation fields only.

ALTER TABLE memory_entries
    ADD COLUMN IF NOT EXISTS memory_type TEXT NOT NULL DEFAULT 'system',
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'archived', 'expired')),
    ADD COLUMN IF NOT EXISTS importance INTEGER NOT NULL DEFAULT 1 CHECK (importance > 0),
    ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS last_accessed_at TIMESTAMPTZ NULL,
    ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ NULL;

CREATE INDEX IF NOT EXISTS idx_memory_entries_user_scope_status
    ON memory_entries (user_id, scope, status);

CREATE INDEX IF NOT EXISTS idx_memory_entries_user_planet_status
    ON memory_entries (user_id, planet_type, status);

CREATE INDEX IF NOT EXISTS idx_memory_entries_user_key_status
    ON memory_entries (user_id, key, status);
