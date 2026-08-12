import tempfile
import unittest
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


class KnowledgeShareGrantTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()
        self.goal = self.api.create_goal(
            {
                "goalName": "Shareable systems study",
                "goalType": "learning",
                "subjects": ["计算机科学"],
                "dailyAvailableMinutes": 30,
            }
        )
        self.document = self.api.create_knowledge_document(
            {
                "fileName": "networking.md",
                "fileType": "markdown",
                "subject": "计算机科学",
                "topic": "网络",
                "goalId": self.goal["id"],
                "content": "TCP uses a reliable byte stream.",
            }
        )
        self.stack = self.api.create_work_tech_stack(
            {"name": "Backend systems", "category": "Engineering", "proficiency": "learning"}
        )

    def test_study_document_is_hidden_from_work_until_granted_then_is_read_only(self):
        self.assertEqual(self.api.list_work_knowledge_documents(), [])
        with self.assertRaises(PermissionError):
            self.api.get_work_knowledge_document(self.document["id"])

        grant = self.api.create_knowledge_share_grant(
            self.document["id"],
            {"sourceGoalId": self.goal["id"], "techStackId": self.stack["id"]},
        )
        listed = self.api.list_work_knowledge_documents(tech_stack_id=self.stack["id"])
        detail = self.api.get_work_knowledge_document(self.document["id"])

        self.assertEqual([item["id"] for item in listed], [self.document["id"]])
        self.assertEqual(listed[0]["accessMode"], "granted")
        self.assertEqual(detail["document"]["id"], self.document["id"])
        self.assertEqual(detail["accessMode"], "granted")
        self.assertEqual(detail["shareGrants"][0]["id"], grant["id"])
        with self.assertRaises(PermissionError):
            self.api.process_work_knowledge_document(self.document["id"])

    def test_revoke_archive_and_source_delete_remove_work_visibility(self):
        first = self.api.create_knowledge_share_grant(
            self.document["id"],
            {"sourceGoalId": self.goal["id"], "techStackId": self.stack["id"]},
        )
        self.api.revoke_knowledge_share_grant(first["id"])
        self.assertEqual(self.api.list_work_knowledge_documents(), [])

        second = self.api.create_knowledge_share_grant(
            self.document["id"],
            {"sourceGoalId": self.goal["id"], "techStackId": self.stack["id"]},
        )
        self.api.delete_work_tech_stack(self.stack["id"])
        self.assertEqual(self.api.list_work_knowledge_documents(), [])
        with self.assertRaises(KeyError):
            self.api.revoke_knowledge_share_grant(second["id"])

        replacement = self.api.create_work_tech_stack(
            {"name": "Runtime systems", "category": "Engineering", "proficiency": "learning"}
        )
        grant = self.api.create_knowledge_share_grant(
            self.document["id"],
            {"sourceGoalId": self.goal["id"], "techStackId": replacement["id"]},
        )
        self.api.delete_knowledge_document(self.document["id"])
        self.assertEqual(self.api.list_work_knowledge_documents(), [])
        with self.assertRaises(KeyError):
            self.api.revoke_knowledge_share_grant(grant["id"])

    def test_unlinked_or_mismatched_goal_documents_cannot_be_shared(self):
        independent = self.api.create_knowledge_document(
            {
                "fileName": "independent.txt",
                "fileType": "txt",
                "subject": "计算机科学",
                "topic": "独立",
                "content": "No source goal.",
            }
        )
        with self.assertRaises(ValueError):
            self.api.create_knowledge_share_grant(
                independent["id"],
                {"sourceGoalId": self.goal["id"], "techStackId": self.stack["id"]},
            )

    def test_changing_the_source_goal_revokes_existing_work_access(self):
        other_goal = self.api.create_goal(
            {
                "goalName": "Other systems study",
                "goalType": "learning",
                "subjects": ["计算机科学"],
                "dailyAvailableMinutes": 30,
            }
        )
        self.api.create_knowledge_share_grant(
            self.document["id"],
            {"sourceGoalId": self.goal["id"], "techStackId": self.stack["id"]},
        )
        self.api.update_knowledge_document(self.document["id"], {"goalId": other_goal["id"]})

        self.assertEqual(self.api.list_work_knowledge_documents(), [])
        self.assertEqual(self.api.list_knowledge_share_grants(self.document["id"]), [])

    def test_tech_stack_detail_uses_explicit_grants_not_keyword_matching(self):
        self.api.create_knowledge_share_grant(
            self.document["id"],
            {"sourceGoalId": self.goal["id"], "techStackId": self.stack["id"]},
        )

        detail = self.api.get_work_tech_stack(self.stack["id"])

        self.assertEqual([item["id"] for item in detail["relatedKnowledge"]], [self.document["id"]])

    def test_sqlite_restart_preserves_grant_without_copying_document(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "share.sqlite3")
            first = ApiFacade(database_path=path)
            goal = first.create_goal(
                {
                    "goalName": "Persistent grant",
                    "goalType": "learning",
                    "subjects": ["系统"],
                    "dailyAvailableMinutes": 30,
                }
            )
            document = first.create_knowledge_document(
                {
                    "fileName": "persistent.txt",
                    "fileType": "txt",
                    "subject": "系统",
                    "topic": "进程",
                    "goalId": goal["id"],
                    "content": "Process isolation.",
                }
            )
            stack = first.create_work_tech_stack(
                {"name": "Operating systems", "category": "Engineering", "proficiency": "learning"}
            )
            first.create_knowledge_share_grant(
                document["id"], {"sourceGoalId": goal["id"], "techStackId": stack["id"]}
            )
            first.persistence.close()

            second = ApiFacade(database_path=path)
            listed = second.list_work_knowledge_documents(tech_stack_id=stack["id"])
            second.persistence.close()

        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["id"], document["id"])
        self.assertEqual(listed[0]["accessMode"], "granted")

    def test_contracts_are_declared(self):
        contracts = {(item["method"], item["path"]) for item in list_contracts()}
        self.assertTrue(
            {
                ("GET", "/api/study/knowledge/documents/{document_id}/share-grants"),
                ("POST", "/api/study/knowledge/documents/{document_id}/share-grants"),
                ("DELETE", "/api/study/knowledge/share-grants/{grant_id}"),
            }
            <= contracts
        )


if __name__ == "__main__":
    unittest.main()
