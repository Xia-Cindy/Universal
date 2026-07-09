import inspect
import unittest
from datetime import timedelta

from backend.app.ai.core import AICoreService
from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_today
from backend.app.planets.study.tutor.service import TutorService


class StudyDomainRefinementTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _goal_payload(self, *, goal_type: str, name: str, deadline=None):
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

    def test_multiple_goals_can_be_created_and_switched(self):
        exam = self.api.create_goal(
            self._goal_payload(
                goal_type="exam",
                name="AI direction graduate exam",
                deadline=(local_today() + timedelta(days=120)).isoformat(),
            )
        )
        reading = self.api.create_goal(
            self._goal_payload(goal_type="reading", name="Read CSAPP", deadline=None)
        )

        goals = self.api.list_goals()
        active_before = self.api.get_active_goal()
        switched = self.api.switch_goal(exam["id"])
        active_after = self.api.get_active_goal()

        self.assertEqual(len(goals), 2)
        self.assertEqual(active_before["id"], reading["id"])
        self.assertEqual(switched["id"], exam["id"])
        self.assertEqual(active_after["id"], exam["id"])
        self.assertEqual({goal["status"] for goal in goals}, {"active"})

    def test_goal_types_and_nullable_deadline(self):
        exam = self.api.create_goal(
            self._goal_payload(
                goal_type="exam",
                name="AI direction graduate exam",
                deadline=(local_today() + timedelta(days=90)).isoformat(),
            )
        )
        learning = self.api.create_goal(
            self._goal_payload(goal_type="learning", name="Learn Python", deadline="")
        )
        reading = self.api.create_goal(
            self._goal_payload(goal_type="reading", name="Read CSAPP", deadline=None)
        )
        growth = self.api.create_goal(
            self._goal_payload(goal_type="growth", name="Become AI Engineer", deadline=None)
        )

        self.assertEqual(exam["goalType"], "exam")
        self.assertIsNotNone(exam["deadline"])
        self.assertIsNone(learning["deadline"])
        self.assertEqual(reading["goalType"], "reading")
        self.assertIsNone(growth["deadline"])

    def test_multiple_plans_and_plan_type_separation(self):
        goal = self.api.create_goal(
            self._goal_payload(goal_type="reading", name="Read CSAPP", deadline=None)
        )

        first_plan = self.api.create_plan({"startDate": local_today().isoformat()})
        second_plan = self.api.create_plan({"startDate": (local_today() + timedelta(days=7)).isoformat()})
        year_plans = [
            plan for plan in self.api.study_repository.year_plans.values() if plan.goal_id == goal["id"]
        ]

        self.assertNotEqual(first_plan["yearPlan"]["id"], second_plan["yearPlan"]["id"])
        self.assertEqual(len(year_plans), 2)
        self.assertEqual(first_plan["yearPlan"]["planType"], "long_term")
        self.assertEqual(first_plan["monthPlans"][0]["planType"], "monthly")
        self.assertEqual(first_plan["weekPlans"][0]["planType"], "weekly")

    def test_knowledge_can_exist_without_goal(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "python-cookbook.txt",
                "fileType": "txt",
                "subject": "python",
                "topic": "recipes",
                "content": "Python Cookbook notes.",
            }
        )

        self.assertIsNone(document["goalId"])

    def test_knowledge_can_link_to_goal_for_future_filtering(self):
        goal = self.api.create_goal(
            self._goal_payload(goal_type="reading", name="Read CSAPP", deadline=None)
        )
        document = self.api.create_knowledge_document(
            {
                "goalId": goal["id"],
                "fileName": "csapp.txt",
                "fileType": "txt",
                "subject": "computer systems",
                "topic": "chapter 3",
                "content": "Machine-level representation notes.",
            }
        )
        detail = self.api.process_knowledge_document(document["id"])
        linked_documents = self.api.list_knowledge_documents(goal_id=goal["id"])

        self.assertEqual(document["goalId"], goal["id"])
        self.assertEqual(linked_documents[0]["id"], document["id"])
        self.assertEqual(detail["chunks"][0]["metadata"]["goalId"], goal["id"])

    def test_existing_tutor_and_analytics_compatibility(self):
        self.api.create_goal(
            self._goal_payload(goal_type="learning", name="Learn Python", deadline=None)
        )
        self.api.create_plan({"startDate": local_today().isoformat()})

        tutor_response = self.api.ask_study_tutor({"question": "What should I study next?"})
        analytics = self.api.get_study_analytics()

        self.assertIn("answer", tutor_response)
        self.assertIn("progressSummary", analytics)
        self.assertIn("dataQuality", analytics)
        self.assertNotIn("RAGFlow", inspect.getsource(TutorService))
        self.assertNotIn("RAGFlow", inspect.getsource(AICoreService))

    def test_milestone_7_5_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("GET", "/api/study/goals"), contracts)
        self.assertIn(("POST", "/api/study/goals/{goal_id}/switch"), contracts)


if __name__ == "__main__":
    unittest.main()
