from backend.app.knowledge.repository import KnowledgeRepository
from backend.app.knowledge.service import KnowledgeService
from backend.app.knowledge.dictionary import (
    EnglishDictionaryService,
    FallbackEnglishDictionaryProvider,
    FreeDictionaryProvider,
    StaticEnglishDictionaryProvider,
)

__all__ = [
    "EnglishDictionaryService",
    "FallbackEnglishDictionaryProvider",
    "FreeDictionaryProvider",
    "KnowledgeRepository",
    "KnowledgeService",
    "StaticEnglishDictionaryProvider",
]
