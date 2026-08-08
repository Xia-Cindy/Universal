import unittest
from datetime import timedelta

from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_now, local_today


class StudyExecutionIdempotencyTests(unittest.TestCase):
    def test_session_finish_retry_keeps_one_event_and_two_memory_records(self):
        api = ApiFacade()
        api.create_onboarding_goal({
            "goalName": "Execution retry", "goalType": "learning", "subjects": ["systems"],
            "currentLevel": "beginner", "dailyAvailableMinutes": 30,
        })
        task = api.create_plan({"startDate": local_today().isoformat()})["dailyTasks"][0]
        start_time = local_now().replace(second=0, microsecond=0)
        session = api.start_execution_session({"taskId": task["id"], "startTime": start_time.isoformat()})["session"]

        api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=15)).isoformat()})
        api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=45)).isoformat()})

        events = api.study_repository.list_learning_events("local-user")
        memory = api.list_memory(planet_type="study", include_inactive=False)
        session_memory = [item for item in memory if item.get("sessionId") == session["id"]]
        planet_memory = [
            item for item in memory
            if item["metadata"].get("sessionId") == session["id"] and item["key"] == "recent_learning_activity"
        ]

        self.assertEqual(len(events), 1)
        self.assertEqual(len(session_memory), 1)
        self.assertEqual(len(planet_memory), 1)


if __name__ == "__main__":
    unittest.main()
