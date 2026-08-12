from __future__ import annotations

from backend.app.models import MemoryEntry
from backend.app.persistence.codec import dumps, loads, memory_from_payload
from backend.app.persistence.sqlite import SQLitePersistence


class SQLiteMemoryRepository:
    def __init__(self, persistence: SQLitePersistence) -> None:
        self._db = persistence

    def save(self, entry: MemoryEntry) -> MemoryEntry:
        with self._db.transaction() as db:
            self.save_in_transaction(db, entry)
        return entry

    def save_in_transaction(self, db, entry: MemoryEntry) -> MemoryEntry:
        payload = entry.to_dict()
        if getattr(self._db, "backend", "sqlite") == "postgres":
            db.execute(
                """INSERT INTO memory_entries
                (id,user_id,scope,planet_type,session_id,key,value,status,importance,payload,created_at,updated_at,last_accessed_at,expires_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                scope=excluded.scope,planet_type=excluded.planet_type,session_id=excluded.session_id,
                key=excluded.key,value=excluded.value,status=excluded.status,importance=excluded.importance,
                payload=excluded.payload,updated_at=excluded.updated_at,
                last_accessed_at=excluded.last_accessed_at,expires_at=excluded.expires_at""",
                (
                    entry.id, entry.user_id, entry.scope.value, entry.planet_type, entry.session_id,
                    entry.key, dumps(entry.value), entry.status.value, entry.importance, dumps(payload),
                    payload["createdAt"], payload["updatedAt"], payload["lastAccessedAt"], payload["expiresAt"],
                ),
            )
        else:
            db.execute(
                """INSERT INTO memory_entries
                (id,user_id,scope,planet_type,session_id,status,importance,payload,created_at,updated_at,last_accessed_at,expires_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                scope=excluded.scope,planet_type=excluded.planet_type,session_id=excluded.session_id,
                status=excluded.status,importance=excluded.importance,payload=excluded.payload,
                updated_at=excluded.updated_at,last_accessed_at=excluded.last_accessed_at,expires_at=excluded.expires_at""",
                (
                    entry.id, entry.user_id, entry.scope.value, entry.planet_type, entry.session_id,
                    entry.status.value, entry.importance, dumps(payload), payload["createdAt"], payload["updatedAt"],
                    payload["lastAccessedAt"], payload["expiresAt"],
                ),
            )
        return entry

    def get(self, memory_id: str, user_id: str) -> MemoryEntry:
        row = self._db.connection.execute("SELECT payload FROM memory_entries WHERE id = ?", (memory_id,)).fetchone()
        if not row:
            raise KeyError(memory_id)
        entry = memory_from_payload(loads(row["payload"]))
        if entry.user_id != user_id:
            raise PermissionError("Memory entry does not belong to user")
        return entry

    def list_for_user(self, user_id: str) -> list[MemoryEntry]:
        rows = self._db.connection.execute(
            "SELECT payload FROM memory_entries WHERE user_id = ? ORDER BY importance DESC, created_at DESC",
            (user_id,),
        ).fetchall()
        return [memory_from_payload(loads(row["payload"])) for row in rows]
