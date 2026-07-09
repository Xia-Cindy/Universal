from backend.app.memory import MemoryService
from backend.app.models import MemoryScope
from backend.app.planets.study.goals import GoalService


class StudyOnboardingService:
    """Study Planet initialization flow backed by the existing Goal model."""

    def __init__(self, *, goals: GoalService, memory: MemoryService) -> None:
        self._goals = goals
        self._memory = memory

    def status(self, user_id: str) -> dict[str, object]:
        goal = self._goals.get_active_goal(user_id)
        return {
            "state": "ready" if goal else "needs_onboarding",
            "activeGoal": goal.to_dict() if goal else None,
        }

    def create_goal(self, user_id: str, payload: dict) -> dict[str, object]:
        goal = self._goals.create_goal(
            user_id,
            {
                "goalName": payload["goalName"],
                "goalType": payload.get("goalType", "learning"),
                "examName": payload.get("examName"),
                "deadline": payload.get("deadline"),
                "description": payload.get("description", ""),
                "subjects": payload["subjects"],
                "currentLevel": payload.get("currentLevel", "unknown"),
                "dailyAvailableMinutes": payload.get("dailyAvailableMinutes", 60),
                "priority": payload.get("priority", "medium"),
            },
        )
        self._write_onboarding_memory(user_id, payload)
        return {
            "state": "ready",
            "activeGoal": goal.to_dict(),
        }

    def _write_onboarding_memory(self, user_id: str, payload: dict) -> None:
        target_direction = payload.get("targetDirection")
        if target_direction:
            self._memory.add(
                user_id=user_id,
                scope=MemoryScope.PLANET,
                planet_type="study",
                key="target_direction",
                value={"target_direction": target_direction},
                memory_type="preference",
                importance=2,
                metadata={"source": "study_onboarding"},
            )
        self._memory.add(
            user_id=user_id,
            scope=MemoryScope.PLANET,
            planet_type="study",
            key="study_preference",
            value={
                "goal_type": payload.get("goalType", "learning"),
                "daily_available_minutes": int(payload.get("dailyAvailableMinutes", 60)),
                "current_level": payload.get("currentLevel", "unknown"),
                "subjects": list(payload.get("subjects", [])),
                "description": payload.get("description", ""),
            },
            memory_type="preference",
            importance=2,
            metadata={"source": "study_onboarding"},
        )
