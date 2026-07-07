from datetime import date

from backend.app.core.dates import local_today, local_now, parse_local_date
from backend.app.memory import MemoryService
from backend.app.models import MemoryScope, StudyGoal
from backend.app.planets.study.repository import StudyRepository


class GoalService:
    def __init__(self, repository: StudyRepository, memory: MemoryService) -> None:
        self._repository = repository
        self._memory = memory

    def create_goal(self, user_id: str, payload: dict) -> StudyGoal:
        deadline = parse_local_date(payload["deadline"])
        self._validate_deadline(deadline)
        goal = StudyGoal(
            user_id=user_id,
            goal_name=payload["goalName"],
            exam_name=payload["examName"],
            deadline=deadline,
            subjects=tuple(payload["subjects"]),
            current_level=payload.get("currentLevel", "unknown"),
            daily_available_minutes=int(payload.get("dailyAvailableMinutes", 60)),
            priority=payload.get("priority", "medium"),
        )
        self._repository.save_goal(goal)
        self._memory.add(
            user_id=user_id,
            scope=MemoryScope.PLANET,
            planet_type="study",
            key="active_goal_id",
            value={"goal_id": goal.id},
        )
        return goal

    def update_goal(self, user_id: str, goal_id: str, payload: dict) -> StudyGoal:
        goal = self._repository.get_goal(goal_id, user_id)
        if "deadline" in payload:
            deadline = parse_local_date(payload["deadline"])
            self._validate_deadline(deadline)
            goal.deadline = deadline
        if "goalName" in payload:
            goal.goal_name = payload["goalName"]
        if "examName" in payload:
            goal.exam_name = payload["examName"]
        if "subjects" in payload:
            goal.subjects = tuple(payload["subjects"])
        if "currentLevel" in payload:
            goal.current_level = payload["currentLevel"]
        if "dailyAvailableMinutes" in payload:
            goal.daily_available_minutes = int(payload["dailyAvailableMinutes"])
        if "priority" in payload:
            goal.priority = payload["priority"]
        goal.updated_at = local_now()
        return self._repository.save_goal(goal)

    def get_active_goal(self, user_id: str) -> StudyGoal | None:
        return self._repository.get_active_goal(user_id)

    def _validate_deadline(self, deadline: date) -> None:
        if deadline < local_today():
            raise ValueError("deadline must not be earlier than today")

