from backend.app.core.dates import local_now, parse_datetime
from backend.app.memory.repository import MemoryRepository
from backend.app.models import MemoryEntry, MemoryScope, MemoryStatus


class MemoryService:
    """Shared Memory Manager with user-owned scoped records."""

    def __init__(self, repository: MemoryRepository | None = None) -> None:
        self._repository = repository or MemoryRepository()

    def add(
        self,
        *,
        user_id: str,
        scope: MemoryScope,
        key: str,
        value: dict,
        planet_type: str | None = None,
        session_id: str | None = None,
        memory_type: str = "system",
        importance: int = 1,
        metadata: dict | None = None,
        expires_at=None,
    ) -> MemoryEntry:
        entry = MemoryEntry(
            user_id=user_id,
            scope=scope,
            key=key,
            value=value,
            planet_type=planet_type,
            session_id=session_id,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {},
            expires_at=parse_datetime(expires_at) if expires_at else None,
        )
        return self._repository.save(entry)

    def create_from_payload(self, user_id: str, payload: dict) -> MemoryEntry:
        return self.add(
            user_id=user_id,
            scope=MemoryScope(payload["scope"]),
            key=payload["key"],
            value=payload["value"],
            planet_type=payload.get("planetType"),
            session_id=payload.get("sessionId"),
            memory_type=payload.get("memoryType", "system"),
            importance=int(payload.get("importance", 1)),
            metadata=payload.get("metadata", {}),
            expires_at=payload.get("expiresAt"),
        )

    def update(self, user_id: str, memory_id: str, payload: dict) -> MemoryEntry:
        entry = self._repository.get(memory_id, user_id)
        if "key" in payload:
            entry.key = payload["key"]
        if "value" in payload:
            entry.value = payload["value"]
        if "memoryType" in payload:
            entry.memory_type = payload["memoryType"]
        if "importance" in payload:
            importance = int(payload["importance"])
            if importance < 1:
                raise ValueError("importance must be greater than zero")
            entry.importance = importance
        if "status" in payload:
            entry.status = MemoryStatus(payload["status"])
        if "metadata" in payload:
            entry.metadata = payload["metadata"]
        if "expiresAt" in payload:
            entry.expires_at = parse_datetime(payload["expiresAt"]) if payload["expiresAt"] else None
        entry.updated_at = local_now()
        return self._repository.save(entry)

    def archive(self, user_id: str, memory_id: str) -> MemoryEntry:
        return self.update(user_id, memory_id, {"status": MemoryStatus.ARCHIVED.value})

    def list_for_user(
        self,
        user_id: str,
        *,
        scope: MemoryScope | None = None,
        planet_type: str | None = None,
        session_id: str | None = None,
        key: str | None = None,
        include_inactive: bool = True,
        mark_accessed: bool = False,
    ) -> list[MemoryEntry]:
        entries = self._repository.list_for_user(user_id)
        entries = self._filter(
            entries,
            scope=scope,
            planet_type=planet_type,
            session_id=session_id,
            key=key,
            include_inactive=include_inactive,
        )
        if mark_accessed:
            for entry in entries:
                entry.last_accessed_at = local_now()
                entry.updated_at = local_now()
                self._repository.save(entry)
        return entries

    def prepare_context(
        self,
        user_id: str,
        *,
        planet_type: str | None = None,
        session_id: str | None = None,
        limit: int = 12,
    ) -> dict[str, object]:
        global_memories = self.list_for_user(
            user_id,
            scope=MemoryScope.GLOBAL,
            include_inactive=False,
            mark_accessed=True,
        )
        planet_memories = (
            self.list_for_user(
                user_id,
                scope=MemoryScope.PLANET,
                planet_type=planet_type,
                include_inactive=False,
                mark_accessed=True,
            )
            if planet_type
            else []
        )
        session_memories = (
            self.list_for_user(
                user_id,
                scope=MemoryScope.SESSION,
                session_id=session_id,
                include_inactive=False,
                mark_accessed=True,
            )
            if session_id
            else []
        )
        return {
            "global": [entry.to_dict() for entry in global_memories[:limit]],
            "planet": [entry.to_dict() for entry in planet_memories[:limit]],
            "session": [entry.to_dict() for entry in session_memories[:limit]],
        }

    def _filter(
        self,
        entries: list[MemoryEntry],
        *,
        scope: MemoryScope | None,
        planet_type: str | None,
        session_id: str | None,
        key: str | None,
        include_inactive: bool,
    ) -> list[MemoryEntry]:
        if scope:
            entries = [entry for entry in entries if entry.scope == scope]
        if planet_type:
            entries = [entry for entry in entries if entry.planet_type == planet_type]
        if session_id:
            entries = [entry for entry in entries if entry.session_id == session_id]
        if key:
            entries = [entry for entry in entries if entry.key == key]
        self._refresh_expired(entries)
        if not include_inactive:
            entries = [entry for entry in entries if entry.status == MemoryStatus.ACTIVE]
        return entries

    def _refresh_expired(self, entries: list[MemoryEntry]) -> None:
        now = local_now()
        for entry in entries:
            if entry.expires_at and entry.expires_at <= now and entry.status == MemoryStatus.ACTIVE:
                entry.status = MemoryStatus.EXPIRED
                entry.updated_at = now
                self._repository.save(entry)
