import tempfile
import unittest
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


class NovelDraftWorkspaceTests(unittest.TestCase):
    def test_draft_create_update_and_ownership_contract(self):
        api = ApiFacade()
        draft = api.create_novel_draft(
            {"title": "星港来信", "synopsis": "一封跨越行星的信。", "content": "# 第一章"}
        )
        updated = api.update_novel_draft(
            draft["id"],
            {"content": "# 第一章\n\n灯塔在清晨熄灭。"},
        )

        self.assertEqual(api.list_novel_drafts()[0]["id"], draft["id"])
        self.assertIn("灯塔", updated["content"])

    def test_sqlite_draft_survives_facade_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "universe.sqlite3")
            first = ApiFacade(database_path=database, persistence_backend="sqlite")
            created = first.create_novel_draft({"title": "持久化草稿", "content": "第一段"})

            second = ApiFacade(database_path=database, persistence_backend="sqlite")
            restored = second.list_novel_drafts()

        self.assertEqual(restored[0]["id"], created["id"])
        self.assertEqual(restored[0]["content"], "第一段")

    def test_contracts_are_declared(self):
        contracts = {(item["method"], item["path"]) for item in list_contracts()}

        self.assertIn(("GET", "/api/novel/drafts"), contracts)
        self.assertIn(("POST", "/api/novel/drafts"), contracts)
        self.assertIn(("PATCH", "/api/novel/drafts/{draft_id}"), contracts)
