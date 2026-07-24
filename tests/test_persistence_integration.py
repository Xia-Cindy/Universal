import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_now, local_today


class SharedPersistenceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "universe.sqlite3")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _goal(self, api, name="Persistent goal"):
        return api.create_goal(
            {
                "goalName": name,
                "goalType": "learning",
                "subjects": ["python"],
                "currentLevel": "beginner",
                "dailyAvailableMinutes": 30,
            }
        )

    def test_restart_preserves_goal_plan_task_session_document_and_memory(self):
        first = ApiFacade(database_path=self.database_path)
        goal = self._goal(first)
        plan = first.create_plan({"startDate": local_today().isoformat()})
        task = plan["dailyTasks"][0]
        started = first.start_execution_session(
            {"taskId": task["id"], "startTime": local_now().replace(second=0, microsecond=0).isoformat()}
        )
        start = local_now().replace(second=0, microsecond=0)
        first.finish_execution_session(
            started["session"]["id"],
            {"endTime": (start + timedelta(minutes=20)).isoformat(), "feeling": "focused"},
        )
        document = first.create_knowledge_document(
            {
                "fileName": "notes.md",
                "fileType": "markdown",
                "subject": "python",
                "topic": "sqlite",
                "goalId": goal["id"],
                "content": "Persistent notes",
            }
        )
        first.process_knowledge_document(document["id"])
        first.create_memory(
            {
                "scope": "planet",
                "planetType": "study",
                "key": "preferred_pace",
                "value": {"value": "steady"},
            }
        )
        first.persistence.close()

        second = ApiFacade(database_path=self.database_path)
        self.assertEqual(second.get_active_goal()["id"], goal["id"])
        self.assertEqual(second.get_current_plan()["yearPlan"]["goalId"], goal["id"])
        self.assertEqual(len(second.list_study_records()), 1)
        self.assertEqual(second.get_knowledge_document(document["id"])["document"]["id"], document["id"])
        self.assertEqual(second.list_memory(planet_type="study")[0]["key"], "preferred_pace")

    def test_current_goal_is_a_context_and_switch_does_not_archive_other_goals(self):
        first = ApiFacade(database_path=self.database_path)
        first_goal = self._goal(first, "First")
        second_goal = self._goal(first, "Second")
        first.switch_goal(first_goal["id"])

        self.assertEqual(first.get_active_goal()["id"], first_goal["id"])
        self.assertEqual(first.get_active_goal()["status"], "active")
        goals = {goal["id"]: goal for goal in first.list_goals()}
        self.assertEqual(goals[second_goal["id"]]["status"], "active")


if __name__ == "__main__":
    unittest.main()
