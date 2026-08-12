from __future__ import annotations

from datetime import timedelta

from backend.app.core.dates import local_now, local_today, parse_local_date
from backend.app.knowledge import KnowledgeService
from backend.app.models import RecallSchedule, RecallSourceType
from backend.app.planets.study.repository import StudyRepository


class StudyRecallService:
    """Explainable, user-adjustable spaced recall for existing Study objects."""

    _REMEMBERED_INTERVALS = (1, 3, 7, 14, 30)

    def __init__(self, repository: StudyRepository, knowledge: KnowledgeService) -> None:
        self._repository = repository
        self._knowledge = knowledge

    def ensure(self, user_id: str, source_type: RecallSourceType, source_id: str) -> RecallSchedule:
        existing = self._repository.get_recall_schedule(user_id, source_type, source_id)
        if existing:
            return existing
        goal_id = self._source_goal_id(user_id, source_type, source_id)
        return self._repository.save_recall_schedule(
            RecallSchedule(
                user_id=user_id,
                source_type=source_type,
                source_id=source_id,
                goal_id=goal_id,
                next_review_date=local_today(),
            )
        )

    def review(
        self,
        user_id: str,
        source_type: RecallSourceType,
        source_id: str,
        *,
        result: str,
    ) -> RecallSchedule:
        if result not in {"remembered", "forgot"}:
            raise ValueError("result must be remembered or forgot")
        schedule = self.ensure(user_id, source_type, source_id)
        now = local_now()
        if schedule.last_reviewed_at and schedule.last_reviewed_at.date() == local_today() and schedule.last_result == result:
            return schedule
        schedule.last_reviewed_at = now
        schedule.last_result = result
        schedule.manually_adjusted = False
        if result == "forgot":
            schedule.review_count = 0
            schedule.interval_days = 0
            schedule.next_review_date = local_today()
            schedule.rationale = "这次记错了，今天再次复习；不会把一次记错视为永久能力判断。"
        else:
            schedule.review_count += 1
            schedule.interval_days = self._REMEMBERED_INTERVALS[
                min(schedule.review_count - 1, len(self._REMEMBERED_INTERVALS) - 1)
            ]
            schedule.next_review_date = local_today() + timedelta(days=schedule.interval_days)
            schedule.rationale = (
                f"连续记住第 {schedule.review_count} 次，按 {schedule.interval_days} 天间隔安排下次复习。"
            )
        schedule.updated_at = now
        return self._repository.save_recall_schedule(schedule)

    def adjust(
        self,
        user_id: str,
        source_type: RecallSourceType,
        source_id: str,
        payload: dict[str, object],
    ) -> RecallSchedule:
        schedule = self.ensure(user_id, source_type, source_id)
        next_review_date = parse_local_date(payload.get("nextReviewDate"))
        if next_review_date < local_today():
            raise ValueError("nextReviewDate must be today or later")
        reason = str(payload.get("reason") or "").strip()
        if not reason:
            raise ValueError("reason is required when adjusting a recall schedule")
        schedule.next_review_date = next_review_date
        schedule.rationale = f"手动调整：{reason}"
        schedule.manually_adjusted = True
        schedule.updated_at = local_now()
        return self._repository.save_recall_schedule(schedule)

    def list(self, user_id: str, *, goal_id: str | None = None) -> list[dict[str, object]]:
        self._bootstrap_existing_sources(user_id)
        schedules = self._repository.list_recall_schedules(user_id, goal_id=goal_id)
        return [schedule.to_dict() for schedule in schedules]

    def for_source(self, user_id: str, source_type: RecallSourceType, source_id: str) -> dict[str, object]:
        return self.ensure(user_id, source_type, source_id).to_dict()

    def _bootstrap_existing_sources(self, user_id: str) -> None:
        for entry in self._repository.list_word_entries(user_id):
            self.ensure(user_id, RecallSourceType.WORD_ENTRY, entry.id)
        for document in self._knowledge.list_documents(user_id):
            for annotation in self._knowledge.list_annotations(user_id, document["id"]):
                if annotation.get("annotationType") == "card":
                    self.ensure(user_id, RecallSourceType.ANNOTATION, str(annotation["id"]))

    def _source_goal_id(self, user_id: str, source_type: RecallSourceType, source_id: str) -> str | None:
        if source_type == RecallSourceType.WORD_ENTRY:
            return self._repository.get_word_entry(source_id, user_id).goal_id
        annotation = self._find_annotation(user_id, source_id)
        return annotation.get("goalId")

    def _find_annotation(self, user_id: str, annotation_id: str) -> dict[str, object]:
        for document in self._knowledge.list_documents(user_id):
            for annotation in self._knowledge.list_annotations(user_id, document["id"]):
                if annotation.get("id") == annotation_id:
                    return annotation
        raise KeyError(annotation_id)
