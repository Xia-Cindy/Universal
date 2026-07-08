import inspect
import unittest
from datetime import timedelta

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_now
from backend.app.memory import MemoryService
from backend.app.models import MemoryScope, MemoryStatus
from backend.app.planets.study.tutor.service import TutorService


class MemoryFoundationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def test_global_planet_and_session_scope_isolation(self):
        memory = MemoryService()
        memory.add(user_id="u1", scope=MemoryScope.GLOBAL, key="language", value={"value": "zh"})
        memory.add(
            user_id="u1",
            scope=MemoryScope.PLANET,
            planet_type="study",
            key="goal",
            value={"value": "MEM"},
        )
        memory.add(
            user_id="u1",
            scope=MemoryScope.SESSION,
            session_id="session-1",
            key="focus",
            value={"value": "algebra"},
        )
        memory.add(user_id="u2", scope=MemoryScope.GLOBAL, key="language", value={"value": "en"})

        self.assertEqual(len(memory.list_for_user("u1", scope=MemoryScope.GLOBAL)), 1)
        self.assertEqual(
            len(memory.list_for_user("u1", scope=MemoryScope.PLANET, planet_type="study")),
            1,
        )
        self.assertEqual(
            len(memory.list_for_user("u1", scope=MemoryScope.SESSION, session_id="session-1")),
            1,
        )
        self.assertEqual(len(memory.list_for_user("u2", scope=MemoryScope.GLOBAL)), 1)

    def test_invalid_scope_rules_are_preserved(self):
        with self.assertRaises(ValueError):
            MemoryService().add(
                user_id="local-user",
                scope=MemoryScope.SESSION,
                key="bad",
                value={},
            )

    def test_lifecycle_filtering_excludes_archived_and_expired_from_context(self):
        memory = MemoryService()
        active = memory.add(
            user_id="local-user",
            scope=MemoryScope.GLOBAL,
            key="active",
            value={"value": True},
        )
        archived = memory.add(
            user_id="local-user",
            scope=MemoryScope.GLOBAL,
            key="archived",
            value={"value": True},
        )
        expired = memory.add(
            user_id="local-user",
            scope=MemoryScope.GLOBAL,
            key="expired",
            value={"value": True},
            expires_at=(local_now() - timedelta(days=1)).isoformat(),
        )
        memory.archive("local-user", archived.id)

        context = memory.prepare_context("local-user")
        keys = [entry["key"] for entry in context["global"]]

        self.assertEqual(keys, ["active"])
        self.assertEqual(active.status, MemoryStatus.ACTIVE)
        self.assertEqual(archived.status, MemoryStatus.ARCHIVED)
        self.assertEqual(expired.status, MemoryStatus.EXPIRED)

    def test_retrieval_updates_access_time(self):
        memory = MemoryService()
        entry = memory.add(
            user_id="local-user",
            scope=MemoryScope.GLOBAL,
            key="preference",
            value={"language": "zh"},
        )

        self.assertIsNone(entry.last_accessed_at)
        memory.list_for_user("local-user", mark_accessed=True)

        self.assertIsNotNone(entry.last_accessed_at)

    def test_context_preparation_returns_relevant_active_memory(self):
        memory = MemoryService()
        memory.add(
            user_id="local-user",
            scope=MemoryScope.GLOBAL,
            key="language",
            value={"value": "zh"},
            importance=2,
        )
        memory.add(
            user_id="local-user",
            scope=MemoryScope.PLANET,
            planet_type="study",
            key="study_style",
            value={"value": "short sessions"},
        )
        memory.add(
            user_id="local-user",
            scope=MemoryScope.SESSION,
            session_id="session-1",
            key="today_focus",
            value={"value": "functions"},
        )

        context = memory.prepare_context(
            "local-user",
            planet_type="study",
            session_id="session-1",
        )

        self.assertEqual(context["global"][0]["key"], "language")
        self.assertEqual(context["planet"][0]["key"], "study_style")
        self.assertEqual(context["session"][0]["key"], "today_focus")

    def test_memory_update_and_archive_api(self):
        created = self.api.create_memory(
            {
                "scope": "global",
                "key": "language",
                "value": {"value": "zh"},
                "importance": 1,
            }
        )

        updated = self.api.update_memory(created["id"], {"importance": 3})
        archived = self.api.archive_memory(created["id"])
        active_memories = self.api.list_memory(include_inactive=False)

        self.assertEqual(updated["importance"], 3)
        self.assertEqual(archived["status"], "archived")
        self.assertEqual(active_memories, [])

    def test_tutor_receives_prepared_memory_context(self):
        self.api.create_memory(
            {
                "scope": "planet",
                "planetType": "study",
                "key": "study_style",
                "value": {"value": "prefers concise explanations"},
                "memoryType": "preference",
            }
        )

        response = self.api.ask_study_tutor({"question": "What should I study?"})

        self.assertTrue(response["memoryContextAvailable"])
        self.assertEqual(response["memoryContext"]["planet"][0]["key"], "study_style")
        self.assertTrue(response["relatedLearningEvent"]["metadata"]["memoryContextAvailable"])
        self.assertNotIn("MemoryService", inspect.getsource(TutorService))

    def test_milestone_5_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("POST", "/api/memory"), contracts)
        self.assertIn(("GET", "/api/memory"), contracts)
        self.assertIn(("PATCH", "/api/memory/{memory_id}"), contracts)
        self.assertIn(("POST", "/api/memory/{memory_id}/archive"), contracts)
        self.assertIn(("GET", "/api/memory/context"), contracts)

    def test_no_autonomous_extraction_or_personality_inference(self):
        service_source = inspect.getsource(MemoryService)

        self.assertNotIn("extract", service_source.lower())
        self.assertNotIn("personality", service_source.lower())
        self.assertNotIn("psychological", service_source.lower())


if __name__ == "__main__":
    unittest.main()
