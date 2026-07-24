from datetime import timedelta

from backend.app.core.dates import local_now, local_today, parse_local_date
from backend.app.models import DailyTask, MonthPlan, TaskStatus, WeekPlan, YearPlan
from backend.app.planets.study.repository import StudyRepository


class PlanService:
    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    def create_plan(self, user_id: str, payload: dict | None = None) -> dict[str, object]:
        payload = payload or {}
        goal = self._repository.get_active_goal(user_id)
        if not goal:
            raise ValueError("active goal is required before creating a plan")

        start_date = parse_local_date(payload.get("startDate", local_today()))
        year = YearPlan(
            user_id=user_id,
            goal_id=goal.id,
            year=start_date.year,
            title=payload.get("title", f"{goal.goal_name} 学习计划"),
        )
        self._repository.save_year_plan(year)

        month = MonthPlan(
            user_id=user_id,
            goal_id=goal.id,
            year_plan_id=year.id,
            month=start_date.month,
            title=payload.get("monthTitle", f"{start_date.month}月学习计划"),
            focus=payload.get("monthFocus", "建立稳定的每日学习节奏。"),
        )
        self._repository.save_month_plan(month)

        week = WeekPlan(
            user_id=user_id,
            goal_id=goal.id,
            month_plan_id=month.id,
            week_start=start_date,
            week_end=start_date + timedelta(days=6),
            title=payload.get("weekTitle", "本周学习重点"),
            focus=payload.get("weekFocus", "完成每日任务，并记录真实学习时间。"),
        )
        self._repository.save_week_plan(week)

        tasks_payload = payload.get("dailyTasks") or self._default_tasks(goal, start_date)
        for task_payload in tasks_payload:
            task = DailyTask(
                user_id=user_id,
                goal_id=goal.id,
                week_plan_id=week.id,
                subject=task_payload["subject"],
                topic=task_payload["topic"],
                task_date=parse_local_date(task_payload["taskDate"]),
                estimated_minutes=int(task_payload.get("estimatedMinutes", goal.daily_available_minutes)),
                priority=task_payload.get("priority", "medium"),
            )
            self._repository.save_daily_task(task)

        return self.get_current_plan(user_id)

    def get_current_plan(self, user_id: str) -> dict[str, object] | None:
        goal = self._repository.get_active_goal(user_id)
        if not goal:
            return None
        plan = self._repository.get_current_plan(user_id, goal.id)
        if not plan:
            return None
        return self._serialize_plan(plan)

    def create_plan_node(self, user_id: str, payload: dict) -> dict[str, object]:
        """Create one node after validating the current Goal parent chain."""
        goal = self._repository.get_active_goal(user_id)
        if not goal:
            raise ValueError("active goal is required before creating a plan node")
        plan_type = payload.get("planType")
        title = str(payload.get("title", "")).strip()
        if not title:
            raise ValueError("plan title is required")
        if plan_type == "long_term":
            self._repository.save_year_plan(
                YearPlan(user_id=user_id, goal_id=goal.id, year=int(payload.get("year", local_today().year)), title=title)
            )
        elif plan_type == "monthly":
            parent_id = payload.get("yearPlanId")
            if not parent_id:
                raise ValueError("monthly plan requires a long term parent")
            parent = self._repository.get_year_plan(parent_id, user_id)
            if parent.goal_id != goal.id:
                raise ValueError("monthly plan parent does not belong to the current goal")
            self._repository.save_month_plan(
                MonthPlan(user_id=user_id, goal_id=goal.id, year_plan_id=parent.id,
                          month=int(payload.get("month", local_today().month)), title=title,
                          focus=str(payload.get("focus", "")).strip())
            )
        elif plan_type == "weekly":
            parent_id = payload.get("monthPlanId")
            if not parent_id:
                raise ValueError("weekly plan requires a monthly parent")
            parent = self._repository.get_month_plan(parent_id, user_id)
            if parent.goal_id != goal.id:
                raise ValueError("weekly plan parent does not belong to the current goal")
            week_start = parse_local_date(payload.get("weekStart", local_today()))
            self._repository.save_week_plan(
                WeekPlan(user_id=user_id, goal_id=goal.id, month_plan_id=parent.id,
                         week_start=week_start, week_end=week_start + timedelta(days=6), title=title,
                         focus=str(payload.get("focus", "")).strip())
            )
        elif plan_type == "daily":
            parent_id = payload.get("weekPlanId")
            if not parent_id:
                raise ValueError("daily task requires a weekly parent")
            parent = self._repository.get_week_plan(parent_id, user_id)
            if parent.goal_id != goal.id:
                raise ValueError("daily task parent does not belong to the current goal")
            subject = str(payload.get("subject", "")).strip()
            topic = str(payload.get("topic", "")).strip()
            if not subject or not topic:
                raise ValueError("daily task requires subject and topic")
            self._repository.save_daily_task(
                DailyTask(user_id=user_id, goal_id=goal.id, week_plan_id=parent.id,
                          subject=subject,
                          topic=topic,
                          task_date=parse_local_date(payload.get("taskDate", local_today())),
                          estimated_minutes=int(payload.get("estimatedMinutes", goal.daily_available_minutes)),
                          priority=str(payload.get("priority", "medium")),
                          sort_order=int(payload.get("sortOrder", 0)))
            )
        else:
            raise ValueError("planType must be long_term, monthly, weekly, or daily")
        return self.get_current_plan(user_id) or {}

    def update_year_plan(self, user_id: str, plan_id: str, payload: dict) -> YearPlan:
        plan = self._repository.get_year_plan(plan_id, user_id)
        if "title" in payload:
            plan.title = payload["title"]
        plan.updated_at = local_now()
        return self._repository.save_year_plan(plan)

    def update_month_plan(self, user_id: str, plan_id: str, payload: dict) -> MonthPlan:
        plan = self._repository.get_month_plan(plan_id, user_id)
        if "title" in payload:
            plan.title = payload["title"]
        if "focus" in payload:
            plan.focus = payload["focus"]
        plan.updated_at = local_now()
        return self._repository.save_month_plan(plan)

    def update_week_plan(self, user_id: str, plan_id: str, payload: dict) -> WeekPlan:
        plan = self._repository.get_week_plan(plan_id, user_id)
        if "title" in payload:
            plan.title = payload["title"]
        if "focus" in payload:
            plan.focus = payload["focus"]
        plan.updated_at = local_now()
        return self._repository.save_week_plan(plan)

    def update_task(self, user_id: str, task_id: str, payload: dict) -> DailyTask:
        task = self._repository.get_task(task_id, user_id)
        if "subject" in payload:
            task.subject = payload["subject"]
        if "topic" in payload:
            task.topic = payload["topic"]
        if "taskDate" in payload:
            task.task_date = parse_local_date(payload["taskDate"])
        if "estimatedMinutes" in payload:
            task.estimated_minutes = int(payload["estimatedMinutes"])
        if "priority" in payload:
            task.priority = payload["priority"]
        if "sortOrder" in payload:
            task.sort_order = int(payload["sortOrder"])
        if "status" in payload:
            task.status = TaskStatus(payload["status"])
            if task.status == TaskStatus.COMPLETED and task.completed_at is None:
                task.completed_at = local_now()
            if task.status != TaskStatus.COMPLETED:
                task.completed_at = None
        task.updated_at = local_now()
        return self._repository.save_daily_task(task)

    def complete_task(self, user_id: str, task_id: str) -> DailyTask:
        task = self._repository.get_task(task_id, user_id)
        if task.status != TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            task.completed_at = local_now()
            task.updated_at = task.completed_at
        return self._repository.save_daily_task(task)

    def _default_tasks(self, goal, start_date):
        subjects = list(goal.subjects) or [goal.goal_name]
        tasks = []
        for offset in range(7):
            subject = subjects[offset % len(subjects)]
            tasks.append(
                {
                    "subject": subject,
                    "topic": f"{subject} 基础",
                    "taskDate": (start_date + timedelta(days=offset)).isoformat(),
                    "estimatedMinutes": goal.daily_available_minutes,
                    "priority": "high" if offset == 0 else "medium",
                }
            )
        return tasks

    def _serialize_plan(self, plan: dict[str, object]) -> dict[str, object]:
        return {
            "yearPlan": plan["yearPlan"].to_dict(),
            "monthPlans": [item.to_dict() for item in plan["monthPlans"]],
            "weekPlans": [item.to_dict() for item in plan["weekPlans"]],
            "dailyTasks": [item.to_dict() for item in plan["dailyTasks"]],
        }
