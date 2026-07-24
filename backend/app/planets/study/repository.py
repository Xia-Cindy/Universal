from datetime import date

from backend.app.models import (
    DailyTask,
    LearningEvent,
    MonthPlan,
    PlanStatus,
    SessionStatus,
    StudyGoal,
    StudySession,
    TaskStatus,
    WeekPlan,
    YearPlan,
    ReviewItem,
    WrongQuestion,
)

from backend.app.persistence.study import SQLiteStudyRepository

__all__ = ["StudyRepository", "SQLiteStudyRepository"]


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
        self.learning_events: dict[str, LearningEvent] = {}
        self.current_goal_ids: dict[tuple[str, str], str] = {}
        self.wrong_questions: dict[str, WrongQuestion] = {}
        self.review_items: dict[str, ReviewItem] = {}

    def save_goal(self, goal: StudyGoal) -> StudyGoal:
        self.goals[goal.id] = goal
        self.current_goal_ids.setdefault((goal.user_id, "study"), goal.id)
        return goal

    def get_goal(self, goal_id: str, user_id: str) -> StudyGoal:
        goal = self.goals[goal_id]
        if goal.user_id != user_id:
            raise PermissionError("Goal does not belong to user")
        return goal

    def get_active_goal(self, user_id: str) -> StudyGoal | None:
        current_goal_id = self.current_goal_ids.get((user_id, "study"))
        if current_goal_id:
            goal = self.goals.get(current_goal_id)
            if goal and goal.user_id == user_id and goal.status.value == "active":
                return goal
        active_goals = [goal for goal in self.goals.values() if goal.user_id == user_id and goal.status.value == "active"]
        if not active_goals:
            return None
        goal = sorted(active_goals, key=lambda item: item.updated_at, reverse=True)[0]
        self.current_goal_ids[(user_id, "study")] = goal.id
        return goal

    def set_current_goal(self, user_id: str, goal_id: str) -> StudyGoal:
        goal = self.get_goal(goal_id, user_id)
        if goal.status.value != "active":
            raise ValueError("Cannot switch to an archived goal")
        self.current_goal_ids[(user_id, "study")] = goal.id
        return goal

    def list_goals(self, user_id: str) -> list[StudyGoal]:
        return sorted(
            [goal for goal in self.goals.values() if goal.user_id == user_id],
            key=lambda goal: goal.updated_at,
            reverse=True,
        )

    def save_year_plan(self, plan: YearPlan) -> YearPlan:
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

    def get_year_plan(self, plan_id: str, user_id: str) -> YearPlan:
        plan = self.year_plans[plan_id]
        if plan.user_id != user_id:
            raise PermissionError("Plan does not belong to user")
        return plan

    def get_month_plan(self, plan_id: str, user_id: str) -> MonthPlan:
        plan = self.month_plans[plan_id]
        if plan.user_id != user_id:
            raise PermissionError("Plan does not belong to user")
        return plan

    def get_week_plan(self, plan_id: str, user_id: str) -> WeekPlan:
        plan = self.week_plans[plan_id]
        if plan.user_id != user_id:
            raise PermissionError("Plan does not belong to user")
        return plan

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

    def list_year_plans_for_goal(self, user_id: str, goal_id: str) -> list[YearPlan]:
        return sorted(
            [
                plan
                for plan in self.year_plans.values()
                if plan.user_id == user_id and plan.goal_id == goal_id
            ],
            key=lambda plan: plan.created_at,
        )

    def list_month_plans_for_goal(self, user_id: str, goal_id: str) -> list[MonthPlan]:
        return sorted(
            [
                plan
                for plan in self.month_plans.values()
                if plan.user_id == user_id and plan.goal_id == goal_id
            ],
            key=lambda plan: (plan.year_plan_id, plan.month, plan.created_at),
        )

    def list_week_plans_for_goal(self, user_id: str, goal_id: str) -> list[WeekPlan]:
        return sorted(
            [
                plan
                for plan in self.week_plans.values()
                if plan.user_id == user_id and plan.goal_id == goal_id
            ],
            key=lambda plan: (plan.week_start, plan.created_at),
        )

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

    def save_learning_event(self, event: LearningEvent) -> LearningEvent:
        self.learning_events[event.id] = event
        return event

    def list_learning_events(self, user_id: str) -> list[LearningEvent]:
        return sorted(
            [event for event in self.learning_events.values() if event.user_id == user_id],
            key=lambda event: event.created_at,
            reverse=True,
        )

    def save_wrong_question(self, question: WrongQuestion) -> WrongQuestion:
        self.wrong_questions[question.id] = question
        return question

    def get_wrong_question(self, question_id: str, user_id: str) -> WrongQuestion:
        question = self.wrong_questions[question_id]
        if question.user_id != user_id:
            raise PermissionError("Wrong question does not belong to user")
        return question

    def list_wrong_questions(self, user_id: str, goal_id: str | None = None) -> list[WrongQuestion]:
        questions = [item for item in self.wrong_questions.values() if item.user_id == user_id]
        if goal_id:
            questions = [item for item in questions if item.goal_id == goal_id]
        return sorted(questions, key=lambda item: item.created_at, reverse=True)

    def save_review_item(self, item: ReviewItem) -> ReviewItem:
        self.review_items[item.id] = item
        return item

    def get_review_item(self, item_id: str, user_id: str) -> ReviewItem:
        item = self.review_items[item_id]
        if item.user_id != user_id:
            raise PermissionError("Review item does not belong to user")
        return item

    def list_review_items(self, user_id: str, wrong_question_id: str | None = None) -> list[ReviewItem]:
        items = [item for item in self.review_items.values() if item.user_id == user_id]
        if wrong_question_id:
            items = [item for item in items if item.wrong_question_id == wrong_question_id]
        return sorted(items, key=lambda item: (item.due_date, item.stage, item.created_at))
