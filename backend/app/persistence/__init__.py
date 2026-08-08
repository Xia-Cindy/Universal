"""Shared persistence boundary for Universe OS."""

from backend.app.persistence.sqlite import SQLitePersistence
from backend.app.persistence.postgres import (
    PostgresKnowledgeRepository,
    PostgresMemoryRepository,
    PostgresNovelRepository,
    PostgresPersistence,
    PostgresStudyRepository,
    PostgresWorkRepository,
)

__all__ = [
    "PostgresKnowledgeRepository",
    "PostgresMemoryRepository",
    "PostgresNovelRepository",
    "PostgresPersistence",
    "PostgresStudyRepository",
    "PostgresWorkRepository",
    "SQLitePersistence",
]
