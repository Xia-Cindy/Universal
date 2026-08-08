"""Shared English dictionary reference for Knowledge and Study Wordbook.

The dictionary is deliberately a Knowledge-side service. Study owns the
learner's word record, while this module owns the external/reference data that
can be attached to that record and represented as a Knowledge document.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from urllib import error, parse, request

from backend.app.core.dates import local_now
from backend.app.models import Document, DocumentChunk, DocumentStatus, DocumentType


DICTIONARY_TAG = "system:english-dictionary"


@dataclass(frozen=True)
class DictionaryLookup:
    status: str
    word: str
    pronunciations: tuple[str, ...] = ()
    usages: tuple[dict[str, str], ...] = ()
    source_name: str = ""
    source_url: str | None = None
    error_message: str | None = None

    def to_dict(self, *, document_id: str | None = None, queried_at: datetime | None = None) -> dict[str, object]:
        return {
            "status": self.status,
            "word": self.word,
            "pronunciations": list(self.pronunciations),
            "usages": [dict(usage) for usage in self.usages],
            "sourceName": self.source_name,
            "sourceUrl": self.source_url,
            "documentId": document_id,
            "errorMessage": self.error_message,
            "queriedAt": (queried_at or local_now()).isoformat(),
        }


class EnglishDictionaryProvider(Protocol):
    def lookup(self, word: str) -> DictionaryLookup:
        """Return an English-English reference record without learner data."""


class StaticEnglishDictionaryProvider:
    """Small offline reference set used when a network dictionary is unavailable.

    This is a continuity layer, not a claim to be a complete English corpus.
    Unknown words remain explicitly unresolved until the remote provider can
    return a real record.
    """

    _entries: dict[str, dict[str, object]] = {
        "allocate": {
            "pronunciation": "/ˈæl.ə.keɪt/",
            "usages": (
                {"partOfSpeech": "verb", "definition": "to give something to a particular person or purpose", "example": "The team allocated more time to testing."},
            ),
        },
        "cache": {
            "pronunciation": "/kæʃ/",
            "usages": (
                {"partOfSpeech": "noun", "definition": "a store of data that can be accessed quickly", "example": "The browser keeps a cache of recently used files."},
                {"partOfSpeech": "verb", "definition": "to store data so it can be used again quickly", "example": "The application caches the result locally."},
            ),
        },
        "context": {
            "pronunciation": "/ˈkɒn.tekst/",
            "usages": (
                {"partOfSpeech": "noun", "definition": "the situation in which something exists or happens", "example": "Read the sentence in context before choosing an answer."},
            ),
        },
        "red": {
            "pronunciation": "/red/",
            "usages": (
                {"partOfSpeech": "adjective", "definition": "having the colour of blood or fire", "example": "The red marker highlights the key idea."},
            ),
        },
        "resilient": {
            "pronunciation": "/rɪˈzɪl.i.ənt/",
            "usages": (
                {"partOfSpeech": "adjective", "definition": "able to become strong, happy, or successful again after difficulty", "example": "A resilient system recovers after a failure."},
            ),
        },
    }

    def lookup(self, word: str) -> DictionaryLookup:
        normalized = _normalize(word)
        entry = self._entries.get(normalized)
        if not entry:
            return DictionaryLookup(status="not_found", word=word, source_name="Universe OS English Dictionary")
        return DictionaryLookup(
            status="available",
            word=word,
            pronunciations=(str(entry["pronunciation"]),),
            usages=tuple(dict(item) for item in entry["usages"]),
            source_name="Universe OS English Dictionary",
        )


class FreeDictionaryProvider:
    """Adapter for a public dictionary API. It is optional and replaceable."""

    def __init__(self, *, base_url: str = "https://api.dictionaryapi.dev/api/v2/entries/en", timeout_seconds: float = 3.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def lookup(self, word: str) -> DictionaryLookup:
        url = f"{self._base_url}/{parse.quote(_normalize(word))}"
        try:
            req = request.Request(url, headers={"Accept": "application/json", "User-Agent": "UniverseOS/1.0"})
            with request.urlopen(req, timeout=self._timeout_seconds) as response:
                raw = response.read().decode("utf-8")
            payload = json.loads(raw)
        except error.HTTPError as exc:
            if exc.code == 404:
                return DictionaryLookup(status="not_found", word=word, source_name="Free Dictionary API", source_url=url)
            return DictionaryLookup(
                status="unavailable",
                word=word,
                source_name="Free Dictionary API",
                source_url=url,
                error_message=f"Dictionary provider returned HTTP {exc.code}",
            )
        except (error.URLError, TimeoutError, ValueError, OSError) as exc:
            return DictionaryLookup(
                status="unavailable",
                word=word,
                source_name="Free Dictionary API",
                source_url=url,
                error_message=f"Dictionary provider is unavailable: {exc}",
            )

        if not isinstance(payload, list) or not payload:
            return DictionaryLookup(status="not_found", word=word, source_name="Free Dictionary API", source_url=url)
        return _lookup_from_free_dictionary_payload(word, payload, source_url=url)


class FallbackEnglishDictionaryProvider:
    """Prefer a local verified record, then try a replaceable remote source."""

    def __init__(self, *, static: EnglishDictionaryProvider | None = None, remote: EnglishDictionaryProvider | None = None) -> None:
        self._static = static or StaticEnglishDictionaryProvider()
        self._remote = remote

    def lookup(self, word: str) -> DictionaryLookup:
        static_result = self._static.lookup(word)
        if static_result.status == "available" or not self._remote:
            return static_result
        remote_result = self._remote.lookup(word)
        if remote_result.status == "available":
            return remote_result
        if remote_result.status == "unavailable" and static_result.status == "not_found":
            return remote_result
        return static_result


class EnglishDictionaryService:
    """Creates the shared dictionary reference and attaches a lookup to a word."""

    def __init__(self, *, repository, provider: EnglishDictionaryProvider) -> None:
        self._repository = repository
        self._provider = provider

    def ensure_reference(self, user_id: str) -> Document:
        for document in self._repository.list_documents(user_id, planet_type="study"):
            if DICTIONARY_TAG in document.tags:
                return document
        document = Document(
            user_id=user_id,
            file_name="English-English Dictionary",
            file_type=DocumentType.MARKDOWN,
            subject="English",
            topic="English-English Dictionary",
            planet_type="study",
            tags=(DICTIONARY_TAG, "reference", "vocabulary"),
            content=(
                "# English-English Dictionary\n\n"
                "This is the shared dictionary reference for Study Wordbook. "
                "When an English word is added or imported, its pronunciation and "
                "dictionary usage records are linked here. Personal meanings, examples, "
                "and notes remain editable in the learner's Wordbook."
            ),
            provider="english_dictionary",
            provider_status="ready",
            processing_status=DocumentStatus.PROCESSED,
        )
        return self._repository.save_document(document)

    def sync(self, user_id: str, *, word: str, language: str) -> dict[str, object]:
        if language.casefold() != "english":
            return DictionaryLookup(
                status="not_applicable",
                word=word,
                source_name="English-English Dictionary",
                error_message="Dictionary sync is available for English entries only.",
            ).to_dict()
        reference = self.ensure_reference(user_id)
        lookup = self._provider.lookup(word)
        result = lookup.to_dict(document_id=reference.id)
        if lookup.status == "available":
            self._upsert_reference_chunk(user_id, reference, result)
        return result

    def _upsert_reference_chunk(self, user_id: str, reference: Document, record: dict[str, object]) -> None:
        normalized = _normalize(str(record["word"]))
        retained = [
            chunk
            for chunk in self._repository.list_chunks(reference.id, user_id)
            if chunk.metadata.get("normalizedWord") != normalized
        ]
        usages = record.get("usages") if isinstance(record.get("usages"), list) else []
        lines = [str(record["word"])]
        pronunciations = record.get("pronunciations") if isinstance(record.get("pronunciations"), list) else []
        if pronunciations:
            lines.append(f"Pronunciation: {', '.join(str(item) for item in pronunciations)}")
        for usage in usages:
            if not isinstance(usage, dict):
                continue
            part = str(usage.get("partOfSpeech") or "usage")
            definition = str(usage.get("definition") or "")
            example = str(usage.get("example") or "")
            lines.append(f"{part}: {definition}")
            if example:
                lines.append(f"Example: {example}")
        retained.append(
            DocumentChunk(
                user_id=user_id,
                document_id=reference.id,
                chunk_index=len(retained),
                content="\n".join(lines),
                metadata={
                    "kind": "dictionary_entry",
                    "normalizedWord": normalized,
                    "sourceName": record.get("sourceName"),
                    "sourceUrl": record.get("sourceUrl"),
                },
            )
        )
        self._repository.replace_chunks(reference.id, retained)


def _lookup_from_free_dictionary_payload(word: str, payload: list[object], *, source_url: str) -> DictionaryLookup:
    pronunciations: list[str] = []
    usages: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        phonetic = item.get("phonetic")
        if isinstance(phonetic, str) and phonetic.strip():
            pronunciations.append(phonetic.strip())
        for phonetics in item.get("phonetics", []):
            if isinstance(phonetics, dict) and isinstance(phonetics.get("text"), str) and phonetics["text"].strip():
                pronunciations.append(phonetics["text"].strip())
        for meaning in item.get("meanings", []):
            if not isinstance(meaning, dict):
                continue
            part = str(meaning.get("partOfSpeech") or "usage")
            for definition in meaning.get("definitions", []):
                if not isinstance(definition, dict) or not definition.get("definition"):
                    continue
                usages.append(
                    {
                        "partOfSpeech": part,
                        "definition": str(definition["definition"]),
                        "example": str(definition.get("example") or ""),
                    }
                )
    if not usages:
        return DictionaryLookup(status="not_found", word=word, source_name="Free Dictionary API", source_url=source_url)
    return DictionaryLookup(
        status="available",
        word=word,
        pronunciations=tuple(dict.fromkeys(pronunciations)),
        usages=tuple(usages[:8]),
        source_name="Free Dictionary API",
        source_url=source_url,
    )


def _normalize(value: str) -> str:
    return " ".join(value.split()).casefold()
