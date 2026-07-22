from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from backend.app.core.dates import local_now


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    CHUNKING = "chunking"
    PROCESSED = "processed"
    FAILED = "failed"


class DocumentType(StrEnum):
    TXT = "txt"
    MARKDOWN = "markdown"
    PDF = "pdf"


def _id() -> str:
    return str(uuid4())


@dataclass
class Document:
    user_id: str
    file_name: str
    file_type: DocumentType
    subject: str
    topic: str
    goal_id: str | None = None
    content: str = ""
    content_encoding: str = "text"
    storage_path: str | None = None
    provider: str = "local"
    provider_dataset_id: str | None = None
    provider_document_id: str | None = None
    provider_status: str | None = None
    processing_status: DocumentStatus = DocumentStatus.UPLOADED
    error_message: str | None = None
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "goalId": self.goal_id,
            "fileName": self.file_name,
            "fileType": self.file_type.value,
            "subject": self.subject,
            "topic": self.topic,
            "storagePath": self.storage_path,
            "contentEncoding": self.content_encoding,
            "provider": self.provider,
            "providerDatasetId": self.provider_dataset_id,
            "providerDocumentId": self.provider_document_id,
            "providerStatus": self.provider_status,
            "processingStatus": self.processing_status.value,
            "errorMessage": self.error_message,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class DocumentChunk:
    user_id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "documentId": self.document_id,
            "chunkIndex": self.chunk_index,
            "content": self.content,
            "metadata": self.metadata,
            "createdAt": self.created_at.isoformat(),
        }


@dataclass
class Concept:
    user_id: str
    subject: str
    topic: str
    name: str
    source: str = "system_placeholder"
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "subject": self.subject,
            "topic": self.topic,
            "name": self.name,
            "source": self.source,
            "createdAt": self.created_at.isoformat(),
        }
