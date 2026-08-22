import tempfile
import unittest
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


class WorkCaseFoundationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def test_case_create_drives_active_case_work_home_and_server_next_action(self):
        created = self.api.create_work_case(
            {
                "title": "企业内部 AI 助手知识问答与运营方案",
                "problem": "知识问答缺少明确的访问边界与运营验证。",
                "goal": "验证最小可运行的知识问答与运营闭环。",
                "scope": "一个 As-Is / To-Be 与一个低资源验证。",
                "nonGoal": "不建设独立监控平台。",
                "successMetrics": ["完成可追溯的 Case brief"],
                "risks": ["资料授权不清晰"],
                "dependencies": ["现有 Universal Knowledge"],
            }
        )

        home = self.api.get_work_home()
        self.assertEqual(created["status"], "active")
        self.assertEqual(created["currentStage"], "discover")
        self.assertEqual(home["activeCase"]["id"], created["id"])
        self.assertEqual(home["currentStage"], "discover")
        self.assertEqual(home["nextAction"]["type"], "continue_case_stage")
        self.assertEqual(home["nextAction"]["route"], f"/work/cases/{created['id']}")
        self.assertEqual(home["caseProgress"]["completedStages"], 0)

    def test_case_stage_progression_is_service_owned_and_cannot_skip(self):
        created = self.api.create_work_case({"title": "Case progression"})
        with self.assertRaisesRegex(ValueError, "one stage at a time"):
            self.api.update_work_case(created["id"], {"currentStage": "govern"})

        updated = self.api.update_work_case(created["id"], {"currentStage": "define"})
        self.assertEqual(updated["currentStage"], "define")
        self.assertEqual(updated["progress"]["completedStages"], 1)

    def test_activating_a_new_case_pauses_the_previous_active_case(self):
        first = self.api.create_work_case({"title": "First active case"})
        second = self.api.create_work_case({"title": "Second active case"})

        cases = {item["id"]: item for item in self.api.list_work_cases()}
        self.assertEqual(cases[first["id"]]["status"], "paused")
        self.assertEqual(cases[second["id"]]["status"], "active")

    def test_case_persists_through_the_shared_sqlite_work_record_store(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = str(Path(directory) / "work-cases.sqlite3")
            first = ApiFacade(database_path=database_path, persistence_backend="sqlite")
            created = first.create_work_case({"title": "Persisted Case"})

            second = ApiFacade(database_path=database_path, persistence_backend="sqlite")
            restored = second.get_work_case(created["id"])

        self.assertEqual(restored["title"], "Persisted Case")
        self.assertEqual(restored["currentStage"], "discover")

    def test_case_contracts_are_declared(self):
        contracts = {(item["method"], item["path"]) for item in list_contracts()}
        self.assertIn(("GET", "/api/work/cases"), contracts)
        self.assertIn(("POST", "/api/work/cases"), contracts)
        self.assertIn(("GET", "/api/work/cases/{case_id}"), contracts)
        self.assertIn(("PATCH", "/api/work/cases/{case_id}"), contracts)

    def test_active_work_ui_has_case_routes_without_a_work_knowledge_entry(self):
        source = (Path(__file__).resolve().parents[1] / "room-portfolio/src/WorkCaseWorkspace.jsx").read_text()
        spaces = (Path(__file__).resolve().parents[1] / "room-portfolio/src/spaces.js").read_text()

        self.assertIn("/work/cases", source)
        self.assertIn("NEXT ACTION · SERVER DECIDED", source)
        self.assertNotIn("work-knowledge", spaces)

    def test_work_case_workspace_owns_a_scrollable_viewport(self):
        stylesheet = (Path(__file__).resolve().parents[1] / "room-portfolio/src/styles/workCaseWorkspace.css").read_text()

        self.assertIn("position: fixed", stylesheet)
        self.assertIn("height: 100dvh", stylesheet)
        self.assertIn("overflow-y: auto", stylesheet)


if __name__ == "__main__":
    unittest.main()
