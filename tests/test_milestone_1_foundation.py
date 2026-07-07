import unittest

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.memory import MemoryService
from backend.app.models import MemoryScope
from backend.app.planet_engine import create_default_registry
from backend.app.planet_engine.registry import PlanetUnavailableError


class PlanetRegistryTests(unittest.TestCase):
    def test_study_is_only_enterable_planet(self):
        registry = create_default_registry()
        planets = registry.list_planets()
        enterable = [planet.name for planet in planets if planet.enterable]

        self.assertEqual(enterable, ["study"])
        self.assertEqual(len(planets), 5)

    def test_future_planets_are_blocked(self):
        registry = create_default_registry()

        with self.assertRaises(PlanetUnavailableError):
            registry.get_enterable_planet("work")


class MemoryScopeTests(unittest.TestCase):
    def test_memory_is_user_owned_and_scope_separated(self):
        memory = MemoryService()
        memory.add(
            user_id="local-user",
            scope=MemoryScope.PLANET,
            planet_type="study",
            key="active_goal_id",
            value={"goal_id": None},
        )

        entries = memory.list_for_user(
            "local-user",
            scope=MemoryScope.PLANET,
            planet_type="study",
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].user_id, "local-user")
        self.assertEqual(entries[0].scope, MemoryScope.PLANET)
        self.assertEqual(entries[0].planet_type, "study")

    def test_planet_memory_requires_planet_type(self):
        with self.assertRaises(ValueError):
            MemoryService().add(
                user_id="local-user",
                scope=MemoryScope.PLANET,
                key="bad",
                value={},
            )


class ApiContractTests(unittest.TestCase):
    def test_milestone_1_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("GET", "/api/health"), contracts)
        self.assertIn(("GET", "/api/planets"), contracts)
        self.assertIn(("GET", "/api/planets/{planet_name}"), contracts)
        self.assertIn(("GET", "/api/study/home"), contracts)

    def test_study_home_empty_state_contract(self):
        payload = ApiFacade().get_study_home()

        self.assertEqual(payload["state"], "empty")
        self.assertEqual(payload["primaryNextAction"]["type"], "create_goal")
        self.assertEqual(payload["progressSnapshot"]["todayStudyMinutes"], 0)


if __name__ == "__main__":
    unittest.main()

