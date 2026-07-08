from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from backend.app.core.dates import local_now


class MemoryScope(StrEnum):
    GLOBAL = "global"
    PLANET = "planet"
    SESSION = "session"


class MemoryStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"


def _id() -> str:
    return str(uuid4())


@dataclass
class MemoryEntry:
    user_id: str
    scope: MemoryScope
    key: str
    value: dict[str, Any]
    memory_type: str = "system"
    status: MemoryStatus = MemoryStatus.ACTIVE
    importance: int = 1
    planet_type: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)
    last_accessed_at: datetime | None = None
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.user_id:
            raise ValueError("user_id is required for every memory entry")
        if self.scope == MemoryScope.PLANET and not self.planet_type:
            raise ValueError("planet_type is required for planet-scoped memory")
        if self.scope == MemoryScope.SESSION and not self.session_id:
            raise ValueError("session_id is required for session-scoped memory")
        if self.importance < 1:
            raise ValueError("importance must be greater than zero")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "scope": self.scope.value,
            "planetType": self.planet_type,
            "sessionId": self.session_id,
            "key": self.key,
            "value": self.value,
            "memoryType": self.memory_type,
            "status": self.status.value,
            "importance": self.importance,
            "metadata": self.metadata,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "lastAccessedAt": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
        }
