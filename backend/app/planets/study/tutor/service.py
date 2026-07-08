from backend.app.ai import AICoreService, AIRequest
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
    ) -> None:
        self._repository = repository
        self._ai_core = ai_core

    def ask(self, *, user: UserProfile, question: str) -> dict[str, object]:
        if not question.strip():
            raise ValueError("question is required")

        goal = self._repository.get_active_goal(user.id)
        plan = self._repository.get_current_plan(user.id, goal.id) if goal else None
        daily_tasks = plan["dailyTasks"] if plan else []
        sessions = self._repository.list_finished_sessions(user.id)
        learning_events = self._repository.list_learning_events(user.id)

        ai_response = self._ai_core.run(
            AIRequest(
                agent_id="study",
                capability="tutor",
                user_question=question,
                context_payload={
                    "user": user.to_dict(),
                    "goal": goal.to_dict() if goal else None,
                    "currentPlan": self._serialize_plan(plan) if plan else None,
                    "dailyTasks": [task.to_dict() for task in daily_tasks],
                    "studySessions": [session.to_dict() for session in sessions],
                    "learningEvents": [event.to_dict() for event in learning_events],
                },
                tool_payloads={
                    "retrieval.search": {
                        "userId": user.id,
                        "query": question,
                        "limit": 3,
                    }
                },
            )
        )
        grounding_chunks = ai_response.metadata.get("groundingChunks", [])
        event = self._repository.save_learning_event(
            LearningEvent(
                user_id=user.id,
                event_type="tutor_interaction",
                summary=question,
                metadata={
                    "question": question,
                    "answer": ai_response.answer,
                    "retrievalInvoked": ai_response.metadata.get("retrievalInvoked", False),
                    "ragInvoked": False,
                    "knowledgeSourcesAvailable": ai_response.metadata.get(
                        "knowledgeSourcesAvailable",
                        False,
                    ),
                    "groundingChunkIds": [
                        chunk["identifiers"]["chunkId"]
                        for chunk in grounding_chunks
                        if "identifiers" in chunk and "chunkId" in chunk["identifiers"]
                    ],
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
