import tempfile
import unittest
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


class ReadingProgressTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()
        self.document = self.api.create_knowledge_document(
            {
                "fileName": "reading.md", "fileType": "markdown", "subject": "reading",
                "topic": "positions", "content": "A durable reading position is not a mastery fact.",
            }
        )

    def test_latest_client_position_is_persisted_and_stale_update_is_rejected(self):
        first = self.api.save_knowledge_reading_progress(
            self.document["id"],
            {"spreadIndex": 4, "pageNumber": 5, "bookmarkLabel": "核心段落", "clientUpdatedAt": "2026-08-13T10:00:00+08:00"},
        )
        stale = self.api.save_knowledge_reading_progress(
            self.document["id"],
            {"spreadIndex": 0, "pageNumber": 1, "clientUpdatedAt": "2026-08-13T09:00:00+08:00"},
        )

        self.assertEqual(first["conflictResolution"], "accepted")
        self.assertEqual(stale["conflictResolution"], "server_newer")
        self.assertEqual(stale["spreadIndex"], 4)
        self.assertEqual(self.api.get_knowledge_reading_progress(self.document["id"])["bookmarkLabel"], "核心段落")

    def test_validation_and_document_delete_keep_progress_out_of_learning_facts(self):
        with self.assertRaises(ValueError):
            self.api.save_knowledge_reading_progress(
                self.document["id"], {"spreadIndex": -1, "pageNumber": 1, "clientUpdatedAt": "2026-08-13T10:00:00+08:00"}
            )
        with self.assertRaises(ValueError):
            self.api.save_knowledge_reading_progress(
                self.document["id"], {"spreadIndex": 0, "pageNumber": 0, "clientUpdatedAt": "2026-08-13T10:00:00+08:00"}
            )
        self.api.save_knowledge_reading_progress(
            self.document["id"], {"spreadIndex": 0, "pageNumber": 1, "clientUpdatedAt": "2026-08-13T10:00:00+08:00"}
        )
        self.assertEqual(self.api.study_repository.list_learning_events("local-user"), [])
        self.api.delete_knowledge_document(self.document["id"])
        with self.assertRaises((KeyError, PermissionError)):
            self.api.get_knowledge_reading_progress(self.document["id"])

    def test_sqlite_restart_preserves_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "progress.sqlite3")
            first = ApiFacade(database_path=path)
            document = first.create_knowledge_document(
                {"fileName": "restart.txt", "fileType": "txt", "subject": "reading", "topic": "restart", "content": "resume"}
            )
            first.save_knowledge_reading_progress(
                document["id"], {"spreadIndex": 2, "pageNumber": 3, "bookmarkLabel": "restart here", "clientUpdatedAt": "2026-08-13T10:00:00+08:00"}
            )
            first.persistence.close()
            second = ApiFacade(database_path=path)
            progress = second.get_knowledge_reading_progress(document["id"])
            second.persistence.close()
        self.assertEqual(progress["spreadIndex"], 2)
        self.assertEqual(progress["bookmarkLabel"], "restart here")

    def test_repository_upsert_does_not_allow_a_stale_first_writer_to_win(self):
        newer = self.api.knowledge.save_reading_progress(
            "local-user", self.document["id"],
            {"spreadIndex": 6, "pageNumber": 7, "clientUpdatedAt": "2026-08-13T12:00:00+08:00"},
        )
        stale = self.api.knowledge.save_reading_progress(
            "local-user", self.document["id"],
            {"spreadIndex": 0, "pageNumber": 1, "clientUpdatedAt": "2026-08-13T11:00:00+08:00"},
        )
        self.assertEqual(newer["conflictResolution"], "accepted")
        self.assertEqual(stale["conflictResolution"], "server_newer")
        self.assertEqual(stale["pageNumber"], 7)

    def test_contracts_are_declared(self):
        contracts = {(item["method"], item["path"]) for item in list_contracts()}
        self.assertTrue({
            ("GET", "/api/study/knowledge/documents/{document_id}/reading-progress"),
            ("PUT", "/api/study/knowledge/documents/{document_id}/reading-progress"),
        } <= contracts)


if __name__ == "__main__":
    unittest.main()
