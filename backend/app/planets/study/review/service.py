from datetime import timedelta

from backend.app.core.dates import local_now, local_today
from backend.app.models import ReviewItem, ReviewStatus, WrongQuestion, WrongQuestionStatus
from backend.app.planets.study.repository import StudyRepository


class ReviewService:
    """Factual Wrong Question and spaced review workflow; no AI required."""

    _INTERVALS = (1, 3, 7, 30)

    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    def create_wrong_question(self, user_id: str, payload: dict) -> dict[str, object]:
        goal_id = payload.get("goalId")
        if goal_id:
            self._repository.get_goal(goal_id, user_id)
        else:
            goal = self._repository.get_active_goal(user_id)
            if not goal:
                raise ValueError("active goal is required before creating a Wrong Question")
            goal_id = goal.id
        question = WrongQuestion(
            user_id=user_id,
            goal_id=goal_id,
            question=str(payload["question"]).strip(),
            correct_answer=str(payload.get("correctAnswer", "")).strip(),
            explanation=str(payload.get("explanation", "")).strip(),
            subject=str(payload.get("subject", "")).strip(),
            topic=str(payload.get("topic", "")).strip(),
            source_event_id=payload.get("sourceEventId"),
        )
        if not question.question:
            raise ValueError("question is required")
        self._repository.save_wrong_question(question)
        created_date = local_today()
        for stage, interval in enumerate(self._INTERVALS, start=1):
            self._repository.save_review_item(
                ReviewItem(
                    user_id=user_id,
                    wrong_question_id=question.id,
                    stage=stage,
                    interval_days=interval,
                    due_date=created_date + timedelta(days=interval),
                )
            )
        return self.detail(user_id, question.id)

    def detail(self, user_id: str, question_id: str) -> dict[str, object]:
        question = self._repository.get_wrong_question(question_id, user_id)
        items = self._repository.list_review_items(user_id, wrong_question_id=question.id)
        return {"wrongQuestion": question.to_dict(), "reviewItems": [item.to_dict() for item in items]}

    def list_wrong_questions(self, user_id: str, goal_id: str | None = None) -> list[dict[str, object]]:
        return [item.to_dict() for item in self._repository.list_wrong_questions(user_id, goal_id)]

    def queue(self, user_id: str, *, include_future: bool = False) -> list[dict[str, object]]:
        today = local_today()
        results = []
        for item in self._repository.list_review_items(user_id):
            if item.status != ReviewStatus.PENDING:
                continue
            if not include_future and item.due_date > today:
                continue
            question = self._repository.get_wrong_question(item.wrong_question_id, user_id)
            results.append({"review": item.to_dict(), "wrongQuestion": question.to_dict()})
        return results

    def complete(self, user_id: str, review_id: str, payload: dict | None = None) -> dict[str, object]:
        item = self._repository.get_review_item(review_id, user_id)
        if item.status == ReviewStatus.COMPLETED:
            return self.detail(user_id, item.wrong_question_id)
        payload = payload or {}
        result = str(payload.get("result", "remembered"))
        if result not in {"remembered", "hard", "forgot", "mastered"}:
            raise ValueError("result must be remembered, hard, forgot, or mastered")
        now = local_now()
        item.status = ReviewStatus.COMPLETED
        item.result = result
        item.completed_at = now
        item.updated_at = now
        self._repository.save_review_item(item)
        question = self._repository.get_wrong_question(item.wrong_question_id, user_id)
        if result == "mastered" and item.stage == len(self._INTERVALS):
            question.status = WrongQuestionStatus.MASTERED
            question.updated_at = now
            self._repository.save_wrong_question(question)
        return self.detail(user_id, question.id)

    def summary(self, user_id: str) -> dict[str, int]:
        items = self._repository.list_review_items(user_id)
        today = local_today()
        pending = [item for item in items if item.status == ReviewStatus.PENDING]
        due = [item for item in pending if item.due_date <= today]
        return {
            "wrongQuestionCount": len(self._repository.list_wrong_questions(user_id)),
            "reviewQueueCount": len(pending),
            "dueReviewCount": len(due),
            "completedReviewCount": sum(item.status == ReviewStatus.COMPLETED for item in items),
        }
