import inspect
import json
import unittest
from datetime import timedelta

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_today
from backend.app.planets.study.workspace.service import StudyWorkspaceService


class StudyWorkspaceApiTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _goal_payload(self, *, name: str, goal_type: str = "learning", deadline=None):
        return {
            "goalType": goal_type,
            "goalName": name,
            "examName": name if goal_type == "exam" else None,
            "deadline": deadline,
            "description": f"{name} description",
            "subjects": [name],
            "currentLevel": "foundation",
            "dailyAvailableMinutes": 45,
            "priority": "medium",
        }

    def test_workspace_returns_empty_state_without_goal(self):
        workspace = self.api.get_study_workspace()

        self.assertEqual(workspace["state"], "needs_goal")
        self.assertIsNone(workspace["currentGoal"])
        self.assertEqual(workspace["goals"], [])
        self.assertEqual(workspace["todayTasks"], [])

    def test_workspace_supports_multiple_goals_and_goal_switching(self):
        exam = self.api.create_goal(
            self._goal_payload(
                name="AI direction exam",
                goal_type="exam",
                deadline=(local_today() + timedelta(days=120)).isoformat(),
            )
        )
        reading = self.api.create_goal(self._goal_payload(name="Read CSAPP", goal_type="reading"))

        workspace_before = self.api.get_study_workspace()
        self.api.switch_goal(exam["id"])
        workspace_after = self.api.get_study_workspace()

        self.assertEqual(len(workspace_before["goals"]), 2)
        self.assertEqual(workspace_before["currentGoal"]["id"], reading["id"])
        self.assertEqual(workspace_after["currentGoal"]["id"], exam["id"])

    def test_workspace_returns_plan_hierarchy_for_current_goal(self):
        goal = self.api.create_goal(self._goal_payload(name="Learn Systems"))
        plan = self.api.create_plan({"startDate": local_today().isoformat()})

        workspace = self.api.get_study_workspace()

        self.assertEqual(workspace["currentGoal"]["id"], goal["id"])
        self.assertEqual(workspace["plans"]["longTermPlans"][0]["id"], plan["yearPlan"]["id"])
        self.assertEqual(workspace["plans"]["monthlyPlans"][0]["planType"], "monthly")
        self.assertEqual(workspace["plans"]["weeklyPlans"][0]["planType"], "weekly")
        self.assertEqual(len(workspace["plans"]["dailyTasks"]), 7)

    def test_workspace_filters_today_tasks_by_current_goal(self):
        first_goal = self.api.create_goal(self._goal_payload(name="Learn Python"))
        first_plan = self.api.create_plan({"startDate": local_today().isoformat()})
        second_goal = self.api.create_goal(self._goal_payload(name="Read CSAPP", goal_type="reading"))
        self.api.create_plan({"startDate": local_today().isoformat()})

        second_workspace = self.api.get_study_workspace()
        self.api.switch_goal(first_goal["id"])
        first_workspace = self.api.get_study_workspace()

        self.assertEqual(second_workspace["currentGoal"]["id"], second_goal["id"])
        self.assertTrue(all(task["goalId"] == second_goal["id"] for task in second_workspace["todayTasks"]))
        self.assertTrue(all(task["goalId"] == first_goal["id"] for task in first_workspace["todayTasks"]))
        self.assertEqual(first_workspace["todayTasks"][0]["id"], first_plan["dailyTasks"][0]["id"])

    def test_workspace_includes_knowledge_goal_relation_summary(self):
        goal = self.api.create_goal(self._goal_payload(name="Read CSAPP", goal_type="reading"))
        independent = self.api.create_knowledge_document(
            {
                "fileName": "general.txt",
                "fileType": "txt",
                "subject": "systems",
                "topic": "general",
                "content": "General systems notes.",
            }
        )
        linked = self.api.create_knowledge_document(
            {
                "goalId": goal["id"],
                "fileName": "csapp.txt",
                "fileType": "txt",
                "subject": "systems",
                "topic": "chapter 1",
                "content": "CSAPP notes.",
            }
        )

        workspace = self.api.get_study_workspace()
        document_ids = {document["id"] for document in workspace["knowledgeSummary"]["documents"]}

        self.assertIn(independent["id"], document_ids)
        self.assertIn(linked["id"], document_ids)
        self.assertEqual(workspace["knowledgeSummary"]["documentCount"], 2)
        self.assertEqual(workspace["knowledgeSummary"]["goalLinkedCount"], 1)
        self.assertEqual(self.api.list_knowledge_documents(goal_id=goal["id"])[0]["id"], linked["id"])

    def test_workspace_api_does_not_redesign_ai_or_planets(self):
        source = inspect.getsource(StudyWorkspaceService)
        workspace_text = json.dumps(self.api.get_study_workspace())
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("GET", "/api/study/workspace"), contracts)
        self.assertNotIn("AICoreService", source)
        self.assertNotIn("RAG", source)
        self.assertNotIn("Work Planet", workspace_text)


if __name__ == "__main__":
    unittest.main()
