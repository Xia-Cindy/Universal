"""Shared persistence boundary for Universe OS."""

from backend.app.persistence.sqlite import SQLitePersistence
from backend.app.persistence.postgres import (
    PostgresKnowledgeRepository,
    PostgresMemoryRepository,
    PostgresPersistence,
    PostgresStudyRepository,
    PostgresWorkRepository,
)

__all__ = [
    "PostgresKnowledgeRepository",
    "PostgresMemoryRepository",
    "PostgresPersistence",
    "PostgresStudyRepository",
    "PostgresWorkRepository",
    "SQLitePersistence",
]
