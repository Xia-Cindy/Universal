from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from backend.app.core.dates import local_now


class EmbeddingStatus(StrEnum):
    PENDING = "pending"
    EMBEDDED = "embedded"
    FAILED = "failed"


def _id() -> str:
    return str(uuid4())


@dataclass(frozen=True)
class EmbeddingResult:
    vector: list[float]
    provider: str
    model: str

    @property
    def dimension(self) -> int:
        return len(self.vector)


@dataclass
class ChunkEmbeddingRecord:
    user_id: str
    document_id: str
    chunk_id: str
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int
    embedding_status: EmbeddingStatus = EmbeddingStatus.PENDING
    embedding_ref: str | None = None
    error_message: str | None = None
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "documentId": self.document_id,
            "chunkId": self.chunk_id,
            "embeddingProvider": self.embedding_provider,
            "embeddingModel": self.embedding_model,
            "embeddingDimension": self.embedding_dimension,
            "embeddingStatus": self.embedding_status.value,
            "embeddingRef": self.embedding_ref,
            "errorMessage": self.error_message,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class RetrievalQuery:
    user_id: str
    query: str
    limit: int = 5
    document_id: str | None = None
    document_ids: tuple[str, ...] = ()
    goal_id: str | None = None
    planet_type: str | None = None


@dataclass(frozen=True)
class RetrievalResult:
    document_id: str
    chunk_id: str
    content: str
    metadata: dict[str, Any]
    score: float
    identifiers: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "documentId": self.document_id,
            "chunkId": self.chunk_id,
            "content": self.content,
            "metadata": self.metadata,
            "score": self.score,
            "identifiers": self.identifiers,
        }
