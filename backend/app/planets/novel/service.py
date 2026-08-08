from backend.app.core.dates import local_now
from backend.app.models import NovelDraft
from backend.app.planets.novel.repository import NovelRepository


class NovelDraftService:
    def __init__(self, repository: NovelRepository) -> None:
        self._repository = repository

    def list_drafts(self, user_id: str) -> list[dict[str, object]]:
        return [draft.to_dict() for draft in self._repository.list(user_id)]

    def create_draft(self, user_id: str, payload: dict) -> dict[str, object]:
        title = str(payload.get("title", "")).strip()
        if not title:
            raise ValueError("Novel title is required")
        draft = NovelDraft(
            user_id=user_id,
            title=title,
            synopsis=str(payload.get("synopsis", "")),
            content=str(payload.get("content", "")),
            status=str(payload.get("status", "draft")),
        )
        return self._repository.save(draft).to_dict()

    def update_draft(self, user_id: str, draft_id: str, payload: dict) -> dict[str, object]:
        draft = self._repository.get(draft_id, user_id)
        if "title" in payload:
            title = str(payload["title"]).strip()
            if not title:
                raise ValueError("Novel title is required")
            draft.title = title
        if "synopsis" in payload:
            draft.synopsis = str(payload["synopsis"])
        if "content" in payload:
            draft.content = str(payload["content"])
        if "status" in payload:
            draft.status = str(payload["status"])
        draft.updated_at = local_now()
        return self._repository.save(draft).to_dict()
