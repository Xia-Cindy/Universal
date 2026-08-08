from __future__ import annotations

from backend.app.models import NovelDraft
from backend.app.persistence.codec import dumps, loads
from backend.app.persistence.sqlite import SQLitePersistence


def _draft_from_payload(payload: dict) -> NovelDraft:
    from backend.app.core.dates import parse_datetime

    return NovelDraft(
        user_id=payload["userId"],
        title=payload["title"],
        synopsis=payload.get("synopsis", ""),
        content=payload.get("content", ""),
        status=payload.get("status", "draft"),
        id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]),
        updated_at=parse_datetime(payload["updatedAt"]),
    )


class NovelRepository:
    def __init__(self) -> None:
        self._drafts: dict[str, NovelDraft] = {}

    def save(self, draft: NovelDraft) -> NovelDraft:
        self._drafts[draft.id] = draft
        return draft

    def get(self, draft_id: str, user_id: str) -> NovelDraft:
        draft = self._drafts[draft_id]
        if draft.user_id != user_id:
            raise PermissionError("Novel draft does not belong to user")
        return draft

    def list(self, user_id: str) -> list[NovelDraft]:
        return sorted(
            (item for item in self._drafts.values() if item.user_id == user_id),
            key=lambda item: item.updated_at,
            reverse=True,
        )


class SQLiteNovelRepository:
    def __init__(self, persistence: SQLitePersistence) -> None:
        self._db = persistence

    def save(self, draft: NovelDraft) -> NovelDraft:
        payload = draft.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO novel_drafts(id,user_id,payload,created_at,updated_at)
                   VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                   payload=excluded.payload,updated_at=excluded.updated_at""",
                (
                    draft.id,
                    draft.user_id,
                    dumps(payload),
                    draft.created_at.isoformat(),
                    draft.updated_at.isoformat(),
                ),
            )
        return draft

    def get(self, draft_id: str, user_id: str) -> NovelDraft:
        row = self._db.connection.execute(
            "SELECT payload FROM novel_drafts WHERE id = ? AND user_id = ?",
            (draft_id, user_id),
        ).fetchone()
        if not row:
            raise KeyError(draft_id)
        return _draft_from_payload(loads(row["payload"]))

    def list(self, user_id: str) -> list[NovelDraft]:
        rows = self._db.connection.execute(
            "SELECT payload FROM novel_drafts WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
        return [_draft_from_payload(loads(row["payload"])) for row in rows]
