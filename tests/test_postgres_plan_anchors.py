import unittest
from datetime import date

from backend.app.models import DailyTask, MonthPlan, WeekPlan, YearPlan
from backend.app.persistence.study import SQLiteStudyRepository


class _Transaction:
    def __init__(self, statements):
        self.statements = statements

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, statement, parameters=()):
        self.statements.append((statement, parameters))


class _PostgresPersistence:
    backend = "postgres"

    def __init__(self):
        self.statements = []

    def transaction(self):
        return _Transaction(self.statements)


class PostgresPlanAnchorTests(unittest.TestCase):
    def setUp(self):
        self.persistence = _PostgresPersistence()
        self.repository = SQLiteStudyRepository(self.persistence)

    def test_week_plan_creates_normalized_parent_anchor(self):
        plan = WeekPlan(
            user_id="user-1",
            goal_id="goal-1",
            month_plan_id="month-1",
            week_start=date(2026, 7, 26),
            week_end=date(2026, 8, 1),
            title="Smoke week",
            focus="Finish the route",
        )

        self.repository.save_week_plan(plan)

        self.assertEqual(len(self.persistence.statements), 2)
        self.assertIn("INSERT INTO study_plans", self.persistence.statements[0][0])
        self.assertIn("INSERT INTO week_plans", self.persistence.statements[1][0])
        self.assertEqual(self.persistence.statements[1][1][0], plan.id)
        self.assertEqual(self.persistence.statements[1][1][3], "month-1")

    def test_month_plan_creates_normalized_parent_anchor(self):
        plan = MonthPlan(
            user_id="user-1",
            goal_id="goal-1",
            year_plan_id="year-1",
            month=7,
            title="Smoke month",
            focus="Read",
        )

        self.repository.save_month_plan(plan)

        self.assertIn("INSERT INTO month_plans", self.persistence.statements[1][0])
        self.assertEqual(self.persistence.statements[1][1][3], "year-1")

    def test_year_plan_creates_normalized_parent_anchor(self):
        plan = YearPlan(user_id="user-1", goal_id="goal-1", year=2026, title="Smoke plan")

        self.repository.save_year_plan(plan)

        self.assertIn("INSERT INTO year_plans", self.persistence.statements[1][0])
        self.assertEqual(self.persistence.statements[1][1][3], 2026)

    def test_task_write_repairs_legacy_parent_anchor_chain(self):
        year = YearPlan(user_id="user-1", goal_id="goal-1", year=2026, title="Year", id="year-1")
        month = MonthPlan(
            user_id="user-1", goal_id="goal-1", year_plan_id=year.id, month=7,
            title="Month", focus="Read", id="month-1",
        )
        week = WeekPlan(
            user_id="user-1", goal_id="goal-1", month_plan_id=month.id,
            week_start=date(2026, 7, 26), week_end=date(2026, 8, 1),
            title="Week", focus="Finish", id="week-1",
        )
        self.repository.get_year_plan = lambda *_: year
        self.repository.get_month_plan = lambda *_: month
        self.repository.get_week_plan = lambda *_: week
        task = DailyTask(
            user_id="user-1", goal_id="goal-1", week_plan_id=week.id,
            subject="systems", topic="Smoke", task_date=date(2026, 7, 26), estimated_minutes=45,
        )

        self.repository.save_daily_task(task)

        statements = [statement for statement, _ in self.persistence.statements]
        self.assertIn("INSERT INTO year_plans", statements[0])
        self.assertIn("INSERT INTO month_plans", statements[1])
        self.assertIn("INSERT INTO week_plans", statements[2])
        self.assertIn("INSERT INTO daily_tasks", statements[3])


if __name__ == "__main__":
    unittest.main()
