import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_today


class StudyRecallV2Tests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()
        self.goal = self.api.create_goal(
            {
                "goalName": "Recall goal",
                "goalType": "learning",
                "subjects": ["英语"],
                "dailyAvailableMinutes": 30,
            }
        )
        self.document = self.api.create_knowledge_document(
            {
                "fileName": "recall.txt",
                "fileType": "txt",
                "subject": "英语",
                "topic": "复习",
                "goalId": self.goal["id"],
                "content": "A source passage for recall scheduling.",
            }
        )

    def test_card_schedule_is_due_then_explains_remembered_and_forgot_results(self):
        card = self.api.create_knowledge_annotation(
            self.document["id"],
            {"selectedText": "source passage", "annotationType": "card"},
        )
        initial = self.api.get_recall_schedule("knowledge_annotation", card["id"])
        remembered = self.api.mark_knowledge_annotation_mastered(
            self.document["id"], card["id"], {"mastered": True}
        )
        repeated = self.api.mark_knowledge_annotation_mastered(
            self.document["id"], card["id"], {"mastered": True}
        )
        forgot = self.api.mark_knowledge_annotation_mastered(
            self.document["id"], card["id"], {"mastered": False}
        )

        self.assertEqual(initial["nextReviewDate"], local_today().isoformat())
        self.assertEqual(remembered["recallSchedule"]["intervalDays"], 1)
        self.assertEqual(repeated["recallSchedule"]["reviewCount"], 1)
        self.assertEqual(forgot["recallSchedule"]["intervalDays"], 0)
        self.assertIn("不会把一次记错", forgot["recallSchedule"]["rationale"])

    def test_word_schedule_can_be_adjusted_without_changing_mastery_progress(self):
        entry = self.api.create_wordbook_entry({"word": "resilient", "goalId": self.goal["id"]})
        created = self.api.get_recall_schedule("wordbook_entry", entry["id"])
        remembered = self.api.review_wordbook_entry(entry["id"], {"remembered": True})
        desired_date = local_today() + timedelta(days=9)
        adjusted = self.api.adjust_recall_schedule(
            "wordbook_entry",
            entry["id"],
            {"nextReviewDate": desired_date.isoformat(), "reason": "考试前集中复习"},
        )
        workspace = self.api.get_study_workspace()

        self.assertEqual(created["nextReviewDate"], local_today().isoformat())
        self.assertEqual(remembered["recallSchedule"]["intervalDays"], 1)
        self.assertEqual(adjusted["nextReviewDate"], desired_date.isoformat())
        self.assertTrue(adjusted["manuallyAdjusted"])
        self.assertIn("考试前集中复习", adjusted["rationale"])
        self.assertEqual(workspace["currentGoal"]["progress"]["masteredItems"], 1)

    def test_repeated_forgotten_word_does_not_duplicate_the_same_review(self):
        entry = self.api.create_wordbook_entry({"word": "retention", "goalId": self.goal["id"]})
        first = self.api.review_wordbook_entry(entry["id"], {"remembered": False})
        repeated = self.api.review_wordbook_entry(entry["id"], {"remembered": False})

        self.assertEqual(first["mistakeCount"], 1)
        self.assertEqual(repeated["mistakeCount"], 1)
        self.assertEqual(repeated["recallSchedule"]["reviewCount"], 0)

    def test_recall_schedules_survive_sqlite_restart_and_filter_by_goal(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "recall.sqlite3")
            first = ApiFacade(database_path=path)
            goal = first.create_goal(
                {
                    "goalName": "Persistent recall",
                    "goalType": "learning",
                    "subjects": ["英语"],
                    "dailyAvailableMinutes": 30,
                }
            )
            entry = first.create_wordbook_entry({"word": "context", "goalId": goal["id"]})
            first.review_wordbook_entry(entry["id"], {"remembered": True})
            first.adjust_recall_schedule(
                "wordbook_entry", entry["id"],
                {"nextReviewDate": (local_today() + timedelta(days=5)).isoformat(), "reason": "周末回顾"},
            )
            first.persistence.close()

            second = ApiFacade(database_path=path)
            schedules = second.list_recall_schedules(goal_id=goal["id"])
            second.persistence.close()

        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0]["sourceId"], entry["id"])
        self.assertEqual(schedules[0]["rationale"], "手动调整：周末回顾")

    def test_contracts_are_declared(self):
        names = {item["name"] for item in list_contracts()}
        self.assertTrue(
            {"list_recall_schedules", "get_recall_schedule", "adjust_recall_schedule"} <= names
        )


if __name__ == "__main__":
    unittest.main()
