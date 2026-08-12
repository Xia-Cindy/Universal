import tempfile
import unittest
from pathlib import Path

from backend.app.api.routes import ApiFacade


class DocumentGoalLinkTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()
        self.first = self.api.create_goal({"goalName": "Goal one", "goalType": "learning", "subjects": ["math"], "dailyAvailableMinutes": 30})
        self.second = self.api.create_goal({"goalName": "Goal two", "goalType": "learning", "subjects": ["math"], "dailyAvailableMinutes": 30})
        self.third = self.api.create_goal({"goalName": "Goal three", "goalType": "learning", "subjects": ["math"], "dailyAvailableMinutes": 30})

    def _create_document(self, *, goal_ids):
        return self.api.create_knowledge_document({
            "fileName": "multi-goal.md", "fileType": "markdown", "subject": "math", "topic": "sets",
            "goalId": goal_ids[0] if goal_ids else None, "goalIds": goal_ids,
            "content": "A set has unique members. Intersections preserve shared members.",
        })

    def test_create_list_and_explicit_link_api_keep_one_primary_and_many_links(self):
        document = self._create_document(goal_ids=[self.first["id"], self.second["id"]])
        self.assertEqual(document["goalId"], self.first["id"])
        self.assertEqual(document["goalIds"], [self.first["id"], self.second["id"]])
        self.assertEqual([item["id"] for item in self.api.list_study_knowledge_documents(goal_id=self.second["id"])], [document["id"]])
        links = self.api.get_knowledge_document_goal_links(document["id"])
        self.assertEqual(links["primaryGoalId"], self.first["id"])
        self.assertEqual(links["goalIds"], [self.first["id"], self.second["id"]])

    def test_replace_links_filters_retrieval_without_copying_or_reprocessing_document(self):
        document = self._create_document(goal_ids=[self.first["id"], self.second["id"]])
        self.api.process_knowledge_document(document["id"])
        self.api.prepare_document_embeddings(document["id"])
        visible = self.api.search_knowledge_chunks({"query": "unique members", "goalId": self.second["id"]})
        isolated = self.api.search_knowledge_chunks({"query": "unique members", "goalId": self.third["id"]})
        self.assertEqual([item["documentId"] for item in visible["results"]], [document["id"]])
        self.assertEqual(isolated["results"], [])
        updated = self.api.replace_knowledge_document_goal_links(
            document["id"], {"primaryGoalId": self.second["id"], "goalIds": [self.second["id"]]}
        )
        self.assertEqual(updated["id"], document["id"])
        self.assertEqual(updated["goalId"], self.second["id"])
        self.assertEqual(updated["processingStatus"], "processed")
        self.assertEqual(self.api.search_knowledge_chunks({"query": "unique members", "goalId": self.first["id"]})["results"], [])

    def test_sqlite_restart_keeps_backed_link_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "links.sqlite3")
            first = ApiFacade(database_path=path)
            one = first.create_goal({"goalName": "Persistent one", "goalType": "learning", "subjects": ["math"], "dailyAvailableMinutes": 30})
            two = first.create_goal({"goalName": "Persistent two", "goalType": "learning", "subjects": ["math"], "dailyAvailableMinutes": 30})
            document = first.create_knowledge_document({"fileName": "persistent.txt", "fileType": "txt", "subject": "math", "topic": "links", "goalId": one["id"], "goalIds": [one["id"], two["id"]], "content": "persistent links"})
            first.persistence.close()
            second = ApiFacade(database_path=path)
            linked = second.get_knowledge_document_goal_links(document["id"])
            listed = second.list_study_knowledge_documents(goal_id=two["id"])
            second.persistence.close()
        self.assertEqual(linked["goalIds"], [one["id"], two["id"]])
        self.assertEqual([item["id"] for item in listed], [document["id"]])


if __name__ == "__main__":
    unittest.main()
