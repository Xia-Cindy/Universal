-- The domain model uses UUID/text MemoryEntry identifiers. Earlier PostgreSQL
-- foundations created a BIGSERIAL key, which prevents shared Memory writes.
ALTER TABLE memory_entries
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id TYPE TEXT USING id::TEXT;
