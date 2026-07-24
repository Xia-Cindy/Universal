import os
import tempfile
import unittest

from backend.app.api.routes import ApiFacade


class ReviewLoopTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()
        self.goal = self.api.create_goal(
            {
                "goalType": "learning",
                "goalName": "Systems review",
                "subjects": ["systems"],
                "currentLevel": "beginner",
                "dailyAvailableMinutes": 30,
                "priority": "high",
            }
        )

    def test_wrong_question_creates_1_3_7_30_queue(self):
        detail = self.api.create_wrong_question(
            {
                "question": "What does a process own?",
                "correctAnswer": "An address space and execution state.",
                "subject": "systems",
                "topic": "processes",
            }
        )

        self.assertEqual([item["intervalDays"] for item in detail["reviewItems"]], [1, 3, 7, 30])
        self.assertEqual(len(self.api.get_review_queue(include_future=True)), 4)

    def test_review_completion_is_idempotent_and_analytics_reads_summary(self):
        detail = self.api.create_wrong_question({"question": "Define a process."})
        review_id = detail["reviewItems"][0]["id"]

        completed = self.api.complete_review_item(review_id, {"result": "remembered"})
        repeated = self.api.complete_review_item(review_id, {"result": "forgot"})

        self.assertEqual(completed["reviewItems"][0]["status"], "completed")
        self.assertEqual(repeated["reviewItems"][0]["result"], "remembered")
        self.assertEqual(self.api.get_study_analytics()["progressSummary"]["review"]["completedReviewCount"], 1)

    def test_review_records_survive_shared_sqlite_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "universe.sqlite3")
            first = ApiFacade(database_path=path)
            goal = first.create_goal(
                {
                    "goalType": "growth",
                    "goalName": "Persistent review",
                    "subjects": [],
                    "currentLevel": "beginner",
                    "dailyAvailableMinutes": 20,
                    "priority": "medium",
                }
            )
            first.create_wrong_question({"question": "Persist this question", "goalId": goal["id"]})
            first.persistence.close()

            second = ApiFacade(database_path=path)
            self.assertEqual(second.list_wrong_questions()[0]["question"], "Persist this question")
            self.assertEqual(len(second.get_review_queue(include_future=True)), 4)
            second.persistence.close()


if __name__ == "__main__":
    unittest.main()
