import csv
import io

from backend.app.core.dates import local_now
from backend.app.models import WordEntry, WordEntrySource


class WordbookService:
    """Study-owned vocabulary records enriched by the shared Knowledge dictionary."""

    def __init__(self, repository, *, dictionary=None) -> None:
        self._repository = repository
        self._dictionary = dictionary

    def list_entries(
        self,
        user_id: str,
        *,
        goal_id: str | None = None,
        language: str | None = None,
        tag: str | None = None,
    ) -> list[dict[str, object]]:
        return [
            entry.to_dict()
            for entry in self._repository.list_word_entries(user_id, goal_id, language, tag)
        ]

    def get_entry(self, user_id: str, entry_id: str) -> dict[str, object]:
        return self._repository.get_word_entry(entry_id, user_id).to_dict()

    def create_entry(self, user_id: str, payload: dict[str, object]) -> dict[str, object]:
        entry = self._entry_from_payload(user_id, payload, source=WordEntrySource.MANUAL)
        existing = self._repository.find_word_entry(user_id, entry.normalized_word, entry.goal_id, entry.language)
        if existing:
            raise ValueError(f"'{entry.word}' is already in this Wordbook scope")
        return self._save_with_dictionary(entry).to_dict()

    def update_entry(self, user_id: str, entry_id: str, payload: dict[str, object]) -> dict[str, object]:
        entry = self._repository.get_word_entry(entry_id, user_id)
        if "word" in payload:
            word = _clean_text(payload["word"])
            if not word:
                raise ValueError("word is required")
            entry.word = word
            entry.normalized_word = _normalize_word(word)
        for field in ("meaning", "pronunciation", "notes"):
            if field in payload:
                setattr(entry, field, _clean_text(payload[field]))
        if "language" in payload:
            entry.language = _language(payload["language"])
        for field in ("tags", "phrases", "examples"):
            if field in payload:
                setattr(entry, field, tuple(_clean_items(payload[field])))
        if "goalId" in payload:
            entry.goal_id = _nullable_text(payload["goalId"])
        duplicate = self._repository.find_word_entry(user_id, entry.normalized_word, entry.goal_id, entry.language)
        if duplicate and duplicate.id != entry.id:
            raise ValueError(f"'{entry.word}' is already in this Wordbook scope")
        entry.updated_at = local_now()
        return self._repository.save_word_entry(entry).to_dict()

    def delete_entry(self, user_id: str, entry_id: str) -> dict[str, object]:
        entry = self._repository.get_word_entry(entry_id, user_id)
        self._repository.delete_word_entry(entry_id, user_id)
        return {"id": entry.id, "deleted": True}

    def refresh_dictionary_entry(self, user_id: str, entry_id: str) -> dict[str, object]:
        entry = self._repository.get_word_entry(entry_id, user_id)
        return self._save_with_dictionary(entry).to_dict()

    def review_entry(
        self,
        user_id: str,
        entry_id: str,
        *,
        remembered: bool,
    ) -> dict[str, object]:
        """Persist the learner's recall result without changing authored content."""
        entry = self._repository.get_word_entry(entry_id, user_id)
        entry.last_reviewed_at = local_now()
        if remembered:
            entry.mastered = True
        else:
            entry.mastered = False
            entry.mistake_count += 1
        entry.updated_at = local_now()
        return self._repository.save_word_entry(entry).to_dict()

    def import_entries(self, user_id: str, payload: dict[str, object]) -> dict[str, object]:
        content = _clean_text(payload.get("content"))
        if not content:
            raise ValueError("import content is required")
        goal_id = _nullable_text(payload.get("goalId"))
        file_name = _clean_text(payload.get("fileName"))
        rows = _csv_rows(content) if file_name.casefold().endswith(".csv") else _text_rows(content)
        imported: list[dict[str, object]] = []
        skipped: list[str] = []
        for row in rows:
            word = _clean_text(row.get("word"))
            if not word:
                continue
            normalized = _normalize_word(word)
            language = _language(payload.get("language"))
            if self._repository.find_word_entry(user_id, normalized, goal_id, language):
                skipped.append(word)
                continue
            entry = self._entry_from_payload(
                user_id,
                {**row, "goalId": goal_id, "language": payload.get("language")},
                source=WordEntrySource.IMPORT,
            )
            imported.append(self._save_with_dictionary(entry).to_dict())
        return {"imported": imported, "importedCount": len(imported), "skipped": skipped, "skippedCount": len(skipped)}

    def _save_with_dictionary(self, entry: WordEntry) -> WordEntry:
        """Attach reference data without replacing learner-authored content."""
        if self._dictionary:
            try:
                dictionary = self._dictionary.sync(
                    entry.user_id,
                    word=entry.word,
                    language=entry.language,
                )
            except (RuntimeError, ValueError, OSError) as exc:
                dictionary = {
                    "status": "unavailable",
                    "word": entry.word,
                    "pronunciations": [],
                    "usages": [],
                    "sourceName": "English-English Dictionary",
                    "sourceUrl": None,
                    "documentId": None,
                    "errorMessage": f"Dictionary sync is unavailable: {exc}",
                    "queriedAt": local_now().isoformat(),
                }
            entry.dictionary = dictionary
            if not entry.pronunciation:
                pronunciations = dictionary.get("pronunciations", [])
                if isinstance(pronunciations, list) and pronunciations:
                    entry.pronunciation = _clean_text(pronunciations[0])
        entry.updated_at = local_now()
        return self._repository.save_word_entry(entry)

    def _entry_from_payload(self, user_id: str, payload: dict[str, object], *, source: WordEntrySource) -> WordEntry:
        word = _clean_text(payload.get("word"))
        if not word:
            raise ValueError("word is required")
        return WordEntry(
            user_id=user_id,
            word=word,
            normalized_word=_normalize_word(word),
            language=_language(payload.get("language")),
            meaning=_clean_text(payload.get("meaning")),
            pronunciation=_clean_text(payload.get("pronunciation")),
            goal_id=_nullable_text(payload.get("goalId")),
            tags=tuple(_clean_items(payload.get("tags", []))),
            phrases=tuple(_clean_items(payload.get("phrases", []))),
            examples=tuple(_clean_items(payload.get("examples", []))),
            notes=_clean_text(payload.get("notes")),
            source=source,
        )


def _text_rows(content: str) -> list[dict[str, object]]:
    rows = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in (line.split("\t") if "\t" in line else line.split("|", 1))]
        rows.append({"word": parts[0], "meaning": parts[1] if len(parts) > 1 else ""})
    return rows


def _csv_rows(content: str) -> list[dict[str, object]]:
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for row in reader:
        if not row:
            continue
        rows.append(
            {
                "word": row.get("word") or row.get("Word") or row.get("term") or "",
                "meaning": row.get("meaning") or row.get("definition") or row.get("translation") or "",
                "pronunciation": row.get("pronunciation") or "",
                "tags": (row.get("tags") or "").split(";"),
            }
        )
    return rows


def _normalize_word(value: str) -> str:
    return " ".join(value.split()).casefold()


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _nullable_text(value: object) -> str | None:
    value = _clean_text(value)
    return value or None


def _language(value: object) -> str:
    return _clean_text(value) or "English"


def _clean_items(value: object) -> list[str]:
    if isinstance(value, str):
        value = value.split(",")
    if not isinstance(value, (list, tuple)):
        return []
    return list(dict.fromkeys(item for item in (_clean_text(item) for item in value) if item))
