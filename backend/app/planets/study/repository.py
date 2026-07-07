from datetime import date

from backend.app.models import (
    DailyTask,
    MonthPlan,
    PlanStatus,
    SessionStatus,
    StudyGoal,
    StudySession,
    TaskStatus,
    WeekPlan,
    YearPlan,
)


class StudyRepository:
    """In-memory Study repository boundary for Milestone 2.

    The database migration defines the durable schema. This repository keeps
    tests and API contracts dependency-light until the PostgreSQL adapter lands.
    """

    def __init__(self) -> None:
        self.goals: dict[str, StudyGoal] = {}
        self.year_plans: dict[str, YearPlan] = {}
        self.month_plans: dict[str, MonthPlan] = {}
        self.week_plans: dict[str, WeekPlan] = {}
        self.daily_tasks: dict[str, DailyTask] = {}
        self.sessions: dict[str, StudySession] = {}

    def save_goal(self, goal: StudyGoal) -> StudyGoal:
        if goal.status.value == "active":
            for existing in self.goals.values():
                if existing.user_id == goal.user_id and existing.id != goal.id:
                    existing.status = type(goal.status).ARCHIVED
        self.goals[goal.id] = goal
        return goal

    def get_goal(self, goal_id: str, user_id: str) -> StudyGoal:
        goal = self.goals[goal_id]
        if goal.user_id != user_id:
            raise PermissionError("Goal does not belong to user")
        return goal

    def get_active_goal(self, user_id: str) -> StudyGoal | None:
        for goal in self.goals.values():
            if goal.user_id == user_id and goal.status.value == "active":
                return goal
        return None

    def save_year_plan(self, plan: YearPlan) -> YearPlan:
        if plan.status == PlanStatus.ACTIVE:
            for existing in self.year_plans.values():
                if existing.user_id == plan.user_id and existing.goal_id == plan.goal_id and existing.id != plan.id:
                    existing.status = PlanStatus.COMPLETED
        self.year_plans[plan.id] = plan
        return plan

    def save_month_plan(self, plan: MonthPlan) -> MonthPlan:
        self.month_plans[plan.id] = plan
        return plan

    def save_week_plan(self, plan: WeekPlan) -> WeekPlan:
        self.week_plans[plan.id] = plan
        return plan

    def save_daily_task(self, task: DailyTask) -> DailyTask:
        self.daily_tasks[task.id] = task
        return task

    def get_task(self, task_id: str, user_id: str) -> DailyTask:
        task = self.daily_tasks[task_id]
        if task.user_id != user_id:
            raise PermissionError("Task does not belong to user")
        return task

    def get_current_plan(self, user_id: str, goal_id: str) -> dict[str, object] | None:
        years = [
            plan
            for plan in self.year_plans.values()
            if plan.user_id == user_id and plan.goal_id == goal_id and plan.status == PlanStatus.ACTIVE
        ]
        if not years:
            return None
        year = sorted(years, key=lambda plan: plan.created_at)[-1]
        months = [plan for plan in self.month_plans.values() if plan.year_plan_id == year.id]
        weeks = [plan for plan in self.week_plans.values() if plan.goal_id == goal_id]
        tasks = [task for task in self.daily_tasks.values() if task.goal_id == goal_id]
        return {
            "yearPlan": year,
            "monthPlans": sorted(months, key=lambda plan: plan.month),
            "weekPlans": sorted(weeks, key=lambda plan: plan.week_start),
            "dailyTasks": sorted(tasks, key=lambda task: (task.task_date, task.created_at)),
        }

    def list_tasks_for_date(self, user_id: str, goal_id: str, task_date: date) -> list[DailyTask]:
        return [
            task
            for task in self.daily_tasks.values()
            if task.user_id == user_id and task.goal_id == goal_id and task.task_date == task_date
        ]

    def list_tasks_for_goal(self, user_id: str, goal_id: str) -> list[DailyTask]:
        return [
            task
            for task in self.daily_tasks.values()
            if task.user_id == user_id and task.goal_id == goal_id
        ]

    def save_session(self, session: StudySession) -> StudySession:
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str, user_id: str) -> StudySession:
        session = self.sessions[session_id]
        if session.user_id != user_id:
            raise PermissionError("Session does not belong to user")
        return session

    def list_finished_sessions(self, user_id: str) -> list[StudySession]:
        return [
            session
            for session in self.sessions.values()
            if session.user_id == user_id and session.status == SessionStatus.FINISHED
        ]

