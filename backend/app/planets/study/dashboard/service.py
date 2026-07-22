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

    def home(
        self,
        *,
        user: UserProfile,
        planet: Planet,
        ai_insight: dict[str, object] | None = None,
        knowledge_status: dict[str, object] | None = None,
    ) -> dict[str, object]:
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
        plan = self._repository.get_current_plan(user.id, goal.id)
        primary_action = self._primary_action(
            has_plan=plan is not None,
            today_tasks=today_tasks,
        )

        progress_summary = {
            "totalTasks": len(all_tasks),
            "completedTasks": len(completed_tasks),
            "taskCompletionRate": round(len(completed_tasks) / len(all_tasks), 2)
            if all_tasks
            else 0,
        }
        progress_snapshot = {
            "todayStudyMinutes": sum(session.duration_minutes for session in today_sessions),
            "weekStudyMinutes": sum(session.duration_minutes for session in week_sessions),
            "studyStreakDays": self._study_streak_days(finished_sessions),
        }
        knowledge_overview = knowledge_status or {}
        analytics_insight = ai_insight or self._empty_ai_insight()

        return {
            "user": user.to_dict(),
            "planet": {
                "name": planet.name,
                "displayName": planet.display_name,
            },
            "state": "ready",
            "currentGoal": {
                **goal.to_dict(),
                "remainingDays": max((goal.deadline - today).days, 0)
                if goal.deadline
                else None,
            },
            "todayTasks": [task.to_dict() for task in today_tasks],
            "primaryNextAction": primary_action,
            "primaryAction": primary_action,
            "aiInsight": analytics_insight,
            "analyticsInsight": analytics_insight,
            "aiRecommendation": analytics_insight,
            "reviewDue": [],
            "recentStudyRecords": [session.to_dict() for session in finished_sessions[:5]],
            "knowledgeStatus": knowledge_overview,
            "knowledgeOverview": knowledge_overview,
            "progressSummary": progress_summary,
            "progressSnapshot": progress_snapshot,
            "progress": {
                **progress_summary,
                **progress_snapshot,
            },
        }

    def _empty_home(self, *, user: UserProfile, planet: Planet) -> dict[str, object]:
        ai_insight = self._empty_ai_insight()
        progress_summary = {
            "totalTasks": 0,
            "completedTasks": 0,
            "taskCompletionRate": 0,
        }
        progress_snapshot = {
            "todayStudyMinutes": 0,
            "weekStudyMinutes": 0,
            "studyStreakDays": 0,
        }
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
                "route": "/study/goals",
                "description": "Start by choosing the learning direction for this Study Workspace.",
            },
            "primaryAction": {
                "type": "create_goal",
                "label": "Create Goal",
                "route": "/study/goals",
                "description": "Start by choosing the learning direction for this Study Workspace.",
            },
            "todayTasks": [],
            "aiInsight": ai_insight,
            "analyticsInsight": ai_insight,
            "aiRecommendation": ai_insight,
            "reviewDue": [],
            "recentStudyRecords": [],
            "knowledgeStatus": {},
            "knowledgeOverview": {},
            "progressSummary": progress_summary,
            "progressSnapshot": progress_snapshot,
            "progress": {
                **progress_summary,
                **progress_snapshot,
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

    def _primary_action(self, *, has_plan: bool, today_tasks) -> dict[str, object]:
        if not has_plan:
            return {
                "type": "create_plan",
                "label": "Create Plan Structure",
                "route": "/study/plan",
                "description": "Turn the current Goal into a long-term, monthly, weekly, and daily route.",
            }
        primary_task = next((task for task in today_tasks if task.status != TaskStatus.COMPLETED), None)
        if primary_task:
            return {
                "type": "start_learning",
                "label": "Start Learning",
                "route": f"/study/session/new?taskId={primary_task.id}",
                "taskId": primary_task.id,
                "description": f"{primary_task.subject}: {primary_task.topic}",
            }
        if today_tasks:
            return {
                "type": "view_analytics",
                "label": "View Analytics",
                "route": "/study/analytics",
                "description": "Today’s tasks are complete. Review the latest learning signal.",
            }
        return {
            "type": "adjust_plan",
            "label": "Add Daily Task",
            "route": "/study/plan",
            "description": "Create or adjust Daily Tasks under the current Goal.",
        }

    def _empty_ai_insight(self) -> dict[str, object]:
        return {
            "learningInsights": [],
            "recommendedActions": [],
            "dataQuality": {
                "state": "insufficient",
                "limitations": ["No Study workflow data is available."],
            },
        }
