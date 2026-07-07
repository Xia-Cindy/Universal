from backend.app.ai import AICoreService, AIRequest, ContextManager
from backend.app.models import LearningEvent
from backend.app.planets.study.repository import StudyRepository
from backend.app.users.service import UserProfile


class TutorService:
    """Study Tutor capability as an AI Core consumer."""

    def __init__(
        self,
        *,
        repository: StudyRepository,
        ai_core: AICoreService,
        context_manager: ContextManager,
    ) -> None:
        self._repository = repository
        self._ai_core = ai_core
        self._context_manager = context_manager

    def ask(self, *, user: UserProfile, question: str) -> dict[str, object]:
        if not question.strip():
            raise ValueError("question is required")

        goal = self._repository.get_active_goal(user.id)
        plan = self._repository.get_current_plan(user.id, goal.id) if goal else None
        daily_tasks = plan["dailyTasks"] if plan else []
        sessions = self._repository.list_finished_sessions(user.id)
        learning_events = self._repository.list_learning_events(user.id)

        context = self._context_manager.build_study_context(
            user=user.to_dict(),
            goal=goal.to_dict() if goal else None,
            current_plan=self._serialize_plan(plan) if plan else None,
            daily_tasks=[task.to_dict() for task in daily_tasks],
            study_sessions=[session.to_dict() for session in sessions],
            learning_events=[event.to_dict() for event in learning_events],
        )
        ai_response = self._ai_core.run(
            AIRequest(
                agent_id="study",
                capability="tutor",
                user_question=question,
                context=context,
            )
        )
        event = self._repository.save_learning_event(
            LearningEvent(
                user_id=user.id,
                event_type="tutor_interaction",
                summary=question,
                metadata={
                    "question": question,
                    "answer": ai_response.answer,
                    "ragInvoked": False,
                    "knowledgeSourcesAvailable": False,
                },
            )
        )
        payload = ai_response.to_dict()
        payload["relatedLearningEvent"] = event.to_dict()
        return payload

    def history(self, *, user: UserProfile) -> list[dict[str, object]]:
        return [event.to_dict() for event in self._repository.list_learning_events(user.id)]

    def _serialize_plan(self, plan: dict[str, object]) -> dict[str, object]:
        return {
            "yearPlan": plan["yearPlan"].to_dict(),
            "monthPlans": [item.to_dict() for item in plan["monthPlans"]],
            "weekPlans": [item.to_dict() for item in plan["weekPlans"]],
            "dailyTasks": [item.to_dict() for item in plan["dailyTasks"]],
        }

