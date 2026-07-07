from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class MemoryScope(StrEnum):
    GLOBAL = "global"
    PLANET = "planet"
    SESSION = "session"


@dataclass(frozen=True)
class MemoryEntry:
    user_id: str
    scope: MemoryScope
    key: str
    value: dict[str, Any]
    planet_type: str | None = None
    session_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.user_id:
            raise ValueError("user_id is required for every memory entry")
        if self.scope == MemoryScope.PLANET and not self.planet_type:
            raise ValueError("planet_type is required for planet-scoped memory")
        if self.scope == MemoryScope.SESSION and not self.session_id:
            raise ValueError("session_id is required for session-scoped memory")

    def to_dict(self) -> dict[str, Any]:
        return {
            "userId": self.user_id,
            "scope": self.scope.value,
            "planetType": self.planet_type,
            "sessionId": self.session_id,
            "key": self.key,
            "value": self.value,
            "createdAt": self.created_at.isoformat(),
        }

