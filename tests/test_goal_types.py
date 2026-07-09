import unittest
from datetime import timedelta

from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_today


class GoalTypesTests(unittest.TestCase):
    def test_exam_goal_preserves_exam_fields(self):
        api = ApiFacade()

        goal = api.create_goal(
            {
                "goalType": "exam",
                "goalName": "AI direction graduate exam",
                "examName": "Graduate Exam",
                "deadline": (local_today() + timedelta(days=120)).isoformat(),
                "description": "Prepare for an AI-focused graduate path.",
                "subjects": ["math", "english"],
                "currentLevel": "foundation",
                "dailyAvailableMinutes": 60,
                "priority": "high",
            }
        )

        self.assertEqual(goal["goalType"], "exam")
        self.assertEqual(goal["examName"], "Graduate Exam")
        self.assertIsNotNone(goal["deadline"])
        self.assertEqual(goal["description"], "Prepare for an AI-focused graduate path.")

    def test_learning_goal_allows_null_deadline_and_no_exam_name(self):
        api = ApiFacade()

        goal = api.create_goal(
            {
                "goalType": "learning",
                "goalName": "Read Computer Systems",
                "deadline": None,
                "description": "Read CSAPP and record chapters.",
                "subjects": ["computer systems"],
                "currentLevel": "beginner",
                "dailyAvailableMinutes": 45,
                "priority": "medium",
            }
        )

        self.assertEqual(goal["goalType"], "learning")
        self.assertIsNone(goal["deadline"])
        self.assertIsNone(goal["examName"])
        self.assertEqual(goal["subjects"], ["computer systems"])

    def test_growth_goal_allows_long_term_cycle(self):
        api = ApiFacade()

        goal = api.create_goal(
            {
                "goalType": "growth",
                "goalName": "Become an AI engineer",
                "deadline": "",
                "description": "Long-term engineering capability growth.",
                "subjects": ["machine learning", "systems", "product engineering"],
                "currentLevel": "working engineer",
                "dailyAvailableMinutes": 30,
                "priority": "high",
            }
        )
        home = api.get_study_home()

        self.assertEqual(goal["goalType"], "growth")
        self.assertIsNone(goal["deadline"])
        self.assertIsNone(home["currentGoal"]["remainingDays"])
        self.assertEqual(home["currentGoal"]["goalName"], "Become an AI engineer")

    def test_invalid_goal_type_is_rejected(self):
        api = ApiFacade()

        with self.assertRaises(ValueError):
            api.create_goal(
                {
                    "goalType": "career",
                    "goalName": "Invalid",
                    "subjects": ["x"],
                    "currentLevel": "x",
                    "dailyAvailableMinutes": 30,
                    "priority": "low",
                }
            )


if __name__ == "__main__":
    unittest.main()
