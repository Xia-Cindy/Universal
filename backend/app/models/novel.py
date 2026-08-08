from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from backend.app.core.dates import local_now


@dataclass
class NovelDraft:
    user_id: str
    title: str
    content: str = ""
    synopsis: str = ""
    status: str = "draft"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "synopsis": self.synopsis,
            "content": self.content,
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
