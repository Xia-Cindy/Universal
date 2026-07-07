-- Milestone 1 foundation schema for Universe OS.
-- Full Study Planet domain tables are introduced in later milestones.

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS planets (
    name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'coming_later')),
    description TEXT NOT NULL,
    primary_action TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS planet_memberships (
    user_id TEXT NOT NULL REFERENCES users(id),
    planet_name TEXT NOT NULL REFERENCES planets(name),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, planet_name)
);

CREATE TABLE IF NOT EXISTS memory_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    scope TEXT NOT NULL CHECK (scope IN ('global', 'planet', 'session')),
    planet_type TEXT NULL,
    session_id TEXT NULL,
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        (scope = 'global' AND planet_type IS NULL AND session_id IS NULL)
        OR (scope = 'planet' AND planet_type IS NOT NULL AND session_id IS NULL)
        OR (scope = 'session' AND session_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_memory_entries_user_scope
    ON memory_entries (user_id, scope);

CREATE INDEX IF NOT EXISTS idx_memory_entries_planet_scope
    ON memory_entries (user_id, planet_type)
    WHERE scope = 'planet';

