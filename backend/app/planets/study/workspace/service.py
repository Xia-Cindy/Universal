from datetime import timedelta

from backend.app.core.dates import local_today
from backend.app.models import Planet, TaskStatus
from backend.app.planets.study.repository import StudyRepository
from backend.app.users.service import UserProfile


class StudyWorkspaceService:
    """Aggregate Study Planet workspace state from existing services."""

    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    def workspace(
        self,
        *,
        user: UserProfile,
        planet: Planet,
        knowledge_summary: dict[str, object],
        analytics_summary: dict[str, object],
    ) -> dict[str, object]:
        today = local_today()
        current_goal = self._repository.get_active_goal(user.id)
        goals = [goal.to_dict() for goal in self._repository.list_goals(user.id)]

        if not current_goal:
            return {
                "user": user.to_dict(),
                "planet": {
                    "name": planet.name,
                    "displayName": planet.display_name,
                },
                "state": "needs_goal",
                "currentGoal": None,
                "goals": goals,
                "plans": self._empty_plans(),
                "planSummary": self._empty_plan_summary(),
                "todayTasks": [],
                "primaryAction": self._primary_action(
                    has_goal=False,
                    has_plan=False,
                    today_tasks=[],
                ),
                "knowledgeSummary": self._knowledge_summary(knowledge_summary),
                "analyticsSummary": analytics_summary,
            }

        all_tasks = self._repository.list_tasks_for_goal(user.id, current_goal.id)
        today_tasks = self._repository.list_tasks_for_date(user.id, current_goal.id, today)
        long_term_plans = self._repository.list_year_plans_for_goal(user.id, current_goal.id)
        finished_sessions = self._repository.list_finished_sessions(user.id)
        week_start = today - timedelta(days=today.weekday())
        current_task_ids = {task.id for task in all_tasks}
        today_minutes = sum(
            session.duration_minutes
            for session in finished_sessions
            if session.task_id in current_task_ids and session.start_time.date() == today
        )
        week_minutes = sum(
            session.duration_minutes
            for session in finished_sessions
            if session.task_id in current_task_ids and week_start <= session.start_time.date() <= today
        )
        completed_tasks = [task for task in all_tasks if task.status == TaskStatus.COMPLETED]

        return {
            "user": user.to_dict(),
            "planet": {
                "name": planet.name,
                "displayName": planet.display_name,
            },
            "state": "ready",
            "currentGoal": {
                **current_goal.to_dict(),
                "remainingDays": max((current_goal.deadline - today).days, 0)
                if current_goal.deadline
                else None,
                "progress": {
                    "totalTasks": len(all_tasks),
                    "completedTasks": len(completed_tasks),
                    "taskCompletionRate": round(len(completed_tasks) / len(all_tasks), 2)
                    if all_tasks
                    else 0,
                },
            },
            "goals": goals,
            "plans": self._plans_for_goal(user.id, current_goal.id),
            "planSummary": self._plan_summary(user.id, current_goal.id),
            "todayTasks": [task.to_dict() for task in today_tasks],
            "primaryAction": self._primary_action(
                has_goal=True,
                has_plan=bool(long_term_plans),
                today_tasks=today_tasks,
            ),
            "knowledgeSummary": self._knowledge_summary(knowledge_summary),
            "analyticsSummary": {
                **analytics_summary,
                "learningSummary": {
                    "todayStudyMinutes": today_minutes,
                    "weekStudyMinutes": week_minutes,
                    "completedTasks": len(completed_tasks),
                    "totalTasks": len(all_tasks),
                    "taskCompletionRate": round(len(completed_tasks) / len(all_tasks), 2)
                    if all_tasks
                    else 0,
                },
            },
        }

    def _plans_for_goal(self, user_id: str, goal_id: str) -> dict[str, object]:
        return {
            "longTermPlans": [
                plan.to_dict()
                for plan in self._repository.list_year_plans_for_goal(user_id, goal_id)
            ],
            "monthlyPlans": [
                plan.to_dict()
                for plan in self._repository.list_month_plans_for_goal(user_id, goal_id)
            ],
            "weeklyPlans": [
                plan.to_dict()
                for plan in self._repository.list_week_plans_for_goal(user_id, goal_id)
            ],
            "dailyTasks": [
                task.to_dict()
                for task in self._repository.list_tasks_for_goal(user_id, goal_id)
            ],
        }

    def _primary_action(
        self,
        *,
        has_goal: bool,
        has_plan: bool,
        today_tasks,
    ) -> dict[str, object]:
        if not has_goal:
            return {
                "type": "create_goal",
                "label": "Create Goal",
                "route": "/study/goals",
                "description": "Start by choosing the learning direction for this Study Workspace.",
            }
        if not has_plan:
            return {
                "type": "create_plan",
                "label": "Create Plan Structure",
                "route": "/study/plan",
                "description": "Turn the current Goal into a long-term, monthly, weekly, and daily route.",
            }
        next_task = next((task for task in today_tasks if task.status != TaskStatus.COMPLETED), None)
        if next_task:
            return {
                "type": "start_learning",
                "label": "Start Learning",
                "route": f"/study/session/new?taskId={next_task.id}",
                "taskId": next_task.id,
                "description": f"{next_task.subject}: {next_task.topic}",
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

    def _plan_summary(self, user_id: str, goal_id: str) -> dict[str, object]:
        long_term_plans = self._repository.list_year_plans_for_goal(user_id, goal_id)
        monthly_plans = self._repository.list_month_plans_for_goal(user_id, goal_id)
        weekly_plans = self._repository.list_week_plans_for_goal(user_id, goal_id)
        daily_tasks = self._repository.list_tasks_for_goal(user_id, goal_id)
        completed_tasks = [task for task in daily_tasks if task.status == TaskStatus.COMPLETED]
        return {
            "hasPlan": bool(long_term_plans),
            "longTermPlanCount": len(long_term_plans),
            "monthlyPlanCount": len(monthly_plans),
            "weeklyPlanCount": len(weekly_plans),
            "dailyTaskCount": len(daily_tasks),
            "completedTaskCount": len(completed_tasks),
            "taskCompletionRate": round(len(completed_tasks) / len(daily_tasks), 2)
            if daily_tasks
            else 0,
        }

    def _knowledge_summary(self, knowledge_summary: dict[str, object]) -> dict[str, object]:
        documents = knowledge_summary.get("documents", [])
        if not isinstance(documents, list):
            documents = []
        return {
            **knowledge_summary,
            "documentCount": len(documents),
            "goalLinkedCount": len([document for document in documents if document.get("goalId")]),
            "independentCount": len([document for document in documents if not document.get("goalId")]),
        }

    def _empty_plans(self) -> dict[str, list[object]]:
        return {
            "longTermPlans": [],
            "monthlyPlans": [],
            "weeklyPlans": [],
            "dailyTasks": [],
        }

    def _empty_plan_summary(self) -> dict[str, object]:
        return {
            "hasPlan": False,
            "longTermPlanCount": 0,
            "monthlyPlanCount": 0,
            "weeklyPlanCount": 0,
            "dailyTaskCount": 0,
            "completedTaskCount": 0,
            "taskCompletionRate": 0,
        }
