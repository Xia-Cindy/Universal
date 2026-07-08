from backend.app.models import MemoryEntry


class MemoryRepository:
    def __init__(self) -> None:
        self.entries: dict[str, MemoryEntry] = {}

    def save(self, entry: MemoryEntry) -> MemoryEntry:
        self.entries[entry.id] = entry
        return entry

    def get(self, memory_id: str, user_id: str) -> MemoryEntry:
        entry = self.entries[memory_id]
        if entry.user_id != user_id:
            raise PermissionError("Memory entry does not belong to user")
        return entry

    def list_for_user(self, user_id: str) -> list[MemoryEntry]:
        return sorted(
            [entry for entry in self.entries.values() if entry.user_id == user_id],
            key=lambda entry: (entry.importance, entry.created_at),
            reverse=True,
        )
