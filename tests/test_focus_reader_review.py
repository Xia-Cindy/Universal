import tempfile
import unittest
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


class FocusReaderReviewTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()
        self.goal = self.api.create_goal(
            {
                "goalName": "英语阅读目标",
                "goalType": "learning",
                "subjects": ["英语"],
                "dailyAvailableMinutes": 30,
            }
        )
        self.document = self.api.create_knowledge_document(
            {
                "fileName": "reading.txt",
                "fileType": "txt",
                "subject": "英语",
                "topic": "阅读",
                "goalId": self.goal["id"],
                "content": "A selected passage for a learner-owned recall card.",
            }
        )

    def test_annotation_inherits_goal_and_mastery_counts_once(self):
        annotation = self.api.create_knowledge_annotation(
            self.document["id"],
            {
                "selectedText": "selected passage",
                "annotationType": "card",
                "hiddenTerms": ["selected", "passage"],
            },
        )
        self.assertEqual(annotation["goalId"], self.goal["id"])
        self.assertEqual(annotation["hiddenTerms"], ["selected", "passage"])

        first = self.api.mark_knowledge_annotation_mastered(
            self.document["id"], annotation["id"], {"mastered": True}
        )
        second = self.api.mark_knowledge_annotation_mastered(
            self.document["id"], annotation["id"], {"mastered": True}
        )
        workspace = self.api.get_study_workspace()

        self.assertTrue(first["mastered"])
        self.assertTrue(second["mastered"])
        self.assertEqual(workspace["currentGoal"]["progress"]["masteredItems"], 1)
        self.assertEqual(
            self.api.get_knowledge_document(self.document["id"])["annotations"][0]["id"],
            annotation["id"],
        )

    def test_wordbook_memory_card_result_tracks_mistakes_and_goal_progress(self):
        entry = self.api.create_wordbook_entry({"word": "resilient", "goalId": self.goal["id"]})
        forgotten = self.api.review_wordbook_entry(entry["id"], {"remembered": False})
        remembered = self.api.review_wordbook_entry(entry["id"], {"remembered": True})
        repeated = self.api.review_wordbook_entry(entry["id"], {"remembered": True})
        workspace = self.api.get_study_workspace()

        self.assertFalse(forgotten["mastered"])
        self.assertEqual(forgotten["mistakeCount"], 1)
        self.assertTrue(remembered["mastered"])
        self.assertTrue(repeated["mastered"])
        self.assertEqual(workspace["currentGoal"]["progress"]["masteredItems"], 1)

    def test_annotations_and_review_state_survive_sqlite_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "focus-reader.sqlite3")
            first = ApiFacade(database_path=path)
            goal = first.create_goal(
                {
                    "goalName": "持久化目标",
                    "goalType": "learning",
                    "subjects": ["英语"],
                    "dailyAvailableMinutes": 30,
                }
            )
            document = first.create_knowledge_document(
                {
                    "fileName": "sample.txt",
                    "fileType": "txt",
                    "subject": "英语",
                    "topic": "阅读",
                    "goalId": goal["id"],
                    "content": "content",
                }
            )
            annotation = first.create_knowledge_annotation(
                document["id"], {"selectedText": "content", "annotationType": "note"}
            )
            first.mark_knowledge_annotation_mastered(document["id"], annotation["id"], {"mastered": True})
            entry = first.create_wordbook_entry({"word": "context", "goalId": goal["id"]})
            first.review_wordbook_entry(entry["id"], {"remembered": False})

            second = ApiFacade(database_path=path)
            detail = second.get_knowledge_document(document["id"])
            restored_entry = second.get_wordbook_entry(entry["id"])

        self.assertTrue(detail["annotations"][0]["mastered"])
        self.assertEqual(restored_entry["mistakeCount"], 1)
        self.assertIsNotNone(restored_entry["lastReviewedAt"])

    def test_focus_reader_contracts_are_declared(self):
        names = {item["name"] for item in list_contracts()}
        self.assertTrue(
            {
                "list_knowledge_annotations",
                "create_knowledge_annotation",
                "update_knowledge_annotation",
                "mark_knowledge_annotation_mastered",
                "delete_knowledge_annotation",
                "review_wordbook_entry",
            }
            <= names
        )


if __name__ == "__main__":
    unittest.main()
