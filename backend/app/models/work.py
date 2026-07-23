from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from backend.app.core.dates import local_now


def _id() -> str:
    return str(uuid4())


@dataclass
class TechStack:
    user_id: str
    name: str
    category: str
    proficiency: str
    description: str = ""
    tags: tuple[str, ...] = ()
    status: str = "active"
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "name": self.name,
            "category": self.category,
            "proficiency": self.proficiency,
            "description": self.description,
            "tags": list(self.tags),
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class WorkProject:
    user_id: str
    title: str
    description: str
    tech_stack_ids: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    status: str = "draft"
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "description": self.description,
            "techStackIds": list(self.tech_stack_ids),
            "evidenceRefs": list(self.evidence_refs),
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class WorkArticle:
    user_id: str
    tech_stack_id: str
    title: str
    content: str
    article_type: str = "knowledge"
    summary: str = ""
    tags: tuple[str, ...] = ()
    status: str = "draft"
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "techStackId": self.tech_stack_id,
            "title": self.title,
            "articleType": self.article_type,
            "summary": self.summary,
            "content": self.content,
            "tags": list(self.tags),
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class WorkLearningRecord:
    user_id: str
    tech_stack_id: str
    title: str
    notes: str
    minutes: int = 0
    tags: tuple[str, ...] = ()
    status: str = "recorded"
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "techStackId": self.tech_stack_id,
            "title": self.title,
            "notes": self.notes,
            "minutes": self.minutes,
            "tags": list(self.tags),
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class ResumeVersion:
    user_id: str
    role_target: str
    title: str
    content: str
    evidence_refs: tuple[str, ...] = ()
    status: str = "draft"
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "roleTarget": self.role_target,
            "title": self.title,
            "content": self.content,
            "evidenceRefs": list(self.evidence_refs),
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
