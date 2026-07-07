from datetime import timedelta

from backend.app.models import Planet
from backend.app.core.dates import local_today
from backend.app.models import SessionStatus, TaskStatus
from backend.app.planets.study.repository import StudyRepository
from backend.app.users.service import UserProfile


class StudyHomeService:
    """Study Home aggregator for the learning workflow layer."""

    def __init__(self, repository: StudyRepository | None = None) -> None:
        self._repository = repository or StudyRepository()

    def home(self, *, user: UserProfile, planet: Planet) -> dict[str, object]:
        today = local_today()
        goal = self._repository.get_active_goal(user.id)
        if not goal:
            return self._empty_home(user=user, planet=planet)

        today_tasks = self._repository.list_tasks_for_date(user.id, goal.id, today)
        all_tasks = self._repository.list_tasks_for_goal(user.id, goal.id)
        finished_sessions = self._repository.list_finished_sessions(user.id)
        today_sessions = [
            session for session in finished_sessions if session.start_time.date() == today
        ]
        week_start = today - timedelta(days=today.weekday())
        week_sessions = [
            session
            for session in finished_sessions
            if week_start <= session.start_time.date() <= today
        ]
        completed_tasks = [task for task in all_tasks if task.status == TaskStatus.COMPLETED]
        primary_task = next((task for task in today_tasks if task.status != TaskStatus.COMPLETED), None)
        primary_action = (
            {
                "type": "start_learning",
                "label": "Start Learning",
                "route": f"/study/session/new?taskId={primary_task.id}",
                "taskId": primary_task.id,
            }
            if primary_task
            else {
                "type": "view_plan",
                "label": "View Plan",
                "route": "/study/plan",
            }
        )

        return {
            "user": user.to_dict(),
            "planet": {
                "name": planet.name,
                "displayName": planet.display_name,
            },
            "state": "ready",
            "currentGoal": goal.to_dict(),
            "todayTasks": [task.to_dict() for task in today_tasks],
            "primaryNextAction": primary_action,
            "aiRecommendation": {
                "status": "placeholder",
                "message": "AI Core starts in Milestone 3. Follow today's plan for now.",
                "basis": "Milestone 2 uses non-AI learning workflow data.",
            },
            "reviewDue": [],
            "recentStudyRecords": [session.to_dict() for session in finished_sessions[:5]],
            "knowledgeStatus": {
                "documents": 0,
                "processed": 0,
                "action": "Knowledge starts in a later milestone.",
            },
            "progressSummary": {
                "totalTasks": len(all_tasks),
                "completedTasks": len(completed_tasks),
                "taskCompletionRate": round(len(completed_tasks) / len(all_tasks), 2)
                if all_tasks
                else 0,
            },
            "progressSnapshot": {
                "todayStudyMinutes": sum(session.duration_minutes for session in today_sessions),
                "weekStudyMinutes": sum(session.duration_minutes for session in week_sessions),
                "studyStreakDays": self._study_streak_days(finished_sessions),
            },
        }

    def _empty_home(self, *, user: UserProfile, planet: Planet) -> dict[str, object]:
        return {
            "user": user.to_dict(),
            "planet": {
                "name": planet.name,
                "displayName": planet.display_name,
            },
            "state": "empty",
            "currentGoal": None,
            "primaryNextAction": {
                "type": "create_goal",
                "label": "Create Goal",
                "route": "/study/plan/goal",
            },
            "todayTasks": [],
            "aiRecommendation": {
                "status": "placeholder",
                "message": "Create your first Goal to unlock personalized study guidance.",
                "basis": "No active Goal exists yet.",
            },
            "reviewDue": [],
            "recentStudyRecords": [],
            "knowledgeStatus": {
                "documents": 0,
                "processed": 0,
                "action": "Upload learning material after creating a Goal.",
            },
            "progressSnapshot": {
                "todayStudyMinutes": 0,
                "weekStudyMinutes": 0,
                "studyStreakDays": 0,
            },
        }

    def _study_streak_days(self, sessions) -> int:
        dates = {session.start_time.date() for session in sessions if session.status == SessionStatus.FINISHED}
        if not dates:
            return 0
        streak = 0
        cursor = local_today()
        while cursor in dates:
            streak += 1
            cursor = cursor - timedelta(days=1)
        return streak
