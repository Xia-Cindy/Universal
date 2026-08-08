import unittest
from datetime import date
from datetime import datetime, timezone

from backend.app.core.dates import LOCAL_TIMEZONE, parse_datetime
from backend.app.persistence.codec import task_from_payload, week_plan_from_payload
from backend.app.persistence.study import SQLiteStudyRepository


class PostgresStudyJsonbCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.repository = object.__new__(SQLiteStudyRepository)

    def test_goal_row_accepts_native_jsonb_subjects(self):
        goal = self.repository._goal_row({
            "id": "goal-jsonb", "user_id": "user-1", "goal_name": "Learn systems",
            "goal_type": "learning", "exam_name": None, "deadline": None,
            "description": "Native JSONB support", "subjects": ["systems", "retrieval"],
            "current_level": "beginner", "daily_available_minutes": 45,
            "priority": "medium", "status": "active",
            "created_at": "2026-07-26T00:00:00+00:00", "updated_at": "2026-07-26T00:00:00+00:00",
        })

        self.assertEqual(goal.subjects, ("systems", "retrieval"))

    def test_learning_event_row_accepts_native_jsonb_metadata(self):
        class Database:
            connection = None

        self.repository._db = Database()
        self.repository._db.connection = type("Connection", (), {
            "execute": lambda *_: type("Result", (), {
                "fetchall": lambda _: [{
                    "id": "event-jsonb", "user_id": "user-1", "event_type": "study",
                    "summary": "Native JSONB support", "metadata": {"source": "smoke"},
                    "created_at": "2026-07-26T00:00:00+00:00",
                }],
            })(),
        })()

        events = self.repository.list_learning_events("user-1")

        self.assertEqual(events[0].metadata, {"source": "smoke"})

    def test_plan_and_task_decoders_accept_native_postgres_dates(self):
        week = week_plan_from_payload({
            "id": "week-1", "userId": "user-1", "goalId": "goal-1", "monthPlanId": "month-1",
            "weekStart": date(2026, 7, 26), "weekEnd": date(2026, 8, 1), "title": "Week",
            "focus": "Read", "planType": "weekly", "status": "active",
            "createdAt": "2026-07-26T00:00:00+00:00", "updatedAt": "2026-07-26T00:00:00+00:00",
        })
        task = task_from_payload({
            "id": "task-1", "userId": "user-1", "goalId": "goal-1", "weekPlanId": "week-1",
            "subject": "systems", "topic": "processes", "taskDate": date(2026, 7, 26),
            "estimatedMinutes": 45, "priority": "medium", "sortOrder": 0, "status": "pending",
            "completedAt": None, "createdAt": "2026-07-26T00:00:00+00:00", "updatedAt": "2026-07-26T00:00:00+00:00",
        })

        self.assertEqual(week.week_start, date(2026, 7, 26))
        self.assertEqual(task.task_date, date(2026, 7, 26))

    def test_native_postgres_timestamp_is_normalized_to_local_timezone(self):
        parsed = parse_datetime(datetime(2026, 7, 26, 16, 5, tzinfo=timezone.utc))

        self.assertEqual(parsed.tzinfo, LOCAL_TIMEZONE)
        self.assertEqual(parsed.date(), date(2026, 7, 27))


if __name__ == "__main__":
    unittest.main()
