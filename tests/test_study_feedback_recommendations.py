import unittest

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_today
from backend.app.models import ReviewItem, WrongQuestion


class StudyFeedbackRecommendationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()
        self.goal = self.api.create_goal(
            {"goalName": "Feedback goal", "goalType": "learning", "subjects": ["math"], "dailyAvailableMinutes": 30}
        )
        self.plan = self.api.create_plan({"startDate": local_today().isoformat()})
        self.document = self.api.create_knowledge_document(
            {"fileName": "feedback.md", "fileType": "markdown", "subject": "math", "topic": "sets", "goalId": self.goal["id"], "content": "facts"}
        )
        self.api.save_knowledge_reading_progress(
            self.document["id"],
            {"spreadIndex": 2, "pageNumber": 3, "clientUpdatedAt": "2026-08-13T12:00:00+08:00"},
        )
        question = WrongQuestion(
            user_id="local-user", goal_id=self.goal["id"], question="What is a set?",
            correct_answer="A collection of unique members.", explanation="Definition", subject="math", topic="sets",
        )
        self.api.study_repository.save_wrong_question(question)
        self.api.study_repository.save_review_item(
            ReviewItem(user_id="local-user", wrong_question_id=question.id, stage=1, interval_days=1, due_date=local_today())
        )

    def test_recommendations_are_traceable_read_only_facts(self):
        task_before = [(task.id, task.status.value) for task in self.api.study_repository.daily_tasks.values()]
        review_before = [(item.id, item.status.value) for item in self.api.study_repository.review_items.values()]
        event_before = list(self.api.study_repository.learning_events)

        result = self.api.get_study_feedback_recommendations()

        self.assertEqual([item["kind"] for item in result["recommendations"]], ["review", "task", "reading"])
        self.assertEqual(result["recommendations"][0]["evidence"][0]["type"], "due_review")
        self.assertEqual(result["recommendations"][1]["evidence"][0]["type"], "incomplete_task")
        self.assertEqual(result["recommendations"][2]["evidence"][0]["pageNumber"], 3)
        self.assertTrue(all(item["requiresConfirmation"] for item in result["recommendations"]))
        self.assertEqual(task_before, [(task.id, task.status.value) for task in self.api.study_repository.daily_tasks.values()])
        self.assertEqual(review_before, [(item.id, item.status.value) for item in self.api.study_repository.review_items.values()])
        self.assertEqual(event_before, list(self.api.study_repository.learning_events))

    def test_recommendations_are_safe_without_an_active_goal(self):
        empty = ApiFacade().get_study_feedback_recommendations()
        self.assertEqual(empty["recommendations"], [])
        self.assertEqual(empty["dataQuality"]["state"], "insufficient")

    def test_contract_is_declared(self):
        contracts = {(item["method"], item["path"]) for item in list_contracts()}
        self.assertIn(("GET", "/api/study/feedback/recommendations"), contracts)


if __name__ == "__main__":
    unittest.main()
