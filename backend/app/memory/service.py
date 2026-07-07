from backend.app.models import MemoryEntry, MemoryScope


class MemoryService:
    """Milestone 1 memory boundary with user-owned scoped records."""

    def __init__(self) -> None:
        self._entries: list[MemoryEntry] = []

    def add(
        self,
        *,
        user_id: str,
        scope: MemoryScope,
        key: str,
        value: dict,
        planet_type: str | None = None,
        session_id: str | None = None,
    ) -> MemoryEntry:
        entry = MemoryEntry(
            user_id=user_id,
            scope=scope,
            key=key,
            value=value,
            planet_type=planet_type,
            session_id=session_id,
        )
        self._entries.append(entry)
        return entry

    def list_for_user(
        self,
        user_id: str,
        *,
        scope: MemoryScope | None = None,
        planet_type: str | None = None,
        session_id: str | None = None,
    ) -> list[MemoryEntry]:
        entries = [entry for entry in self._entries if entry.user_id == user_id]
        if scope:
            entries = [entry for entry in entries if entry.scope == scope]
        if planet_type:
            entries = [entry for entry in entries if entry.planet_type == planet_type]
        if session_id:
            entries = [entry for entry in entries if entry.session_id == session_id]
        return entries

