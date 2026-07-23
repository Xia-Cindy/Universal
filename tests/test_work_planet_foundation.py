import unittest
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class WorkPlanetFoundationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def test_work_planet_is_enterable(self):
        planets = self.api.list_planets()["planets"]
        work = next(planet for planet in planets if planet["name"] == "work")

        self.assertTrue(work["enterable"])
        self.assertEqual(work["status"], "active")
        self.assertEqual(work["primaryAction"], "Enter Work Planet")

    def test_work_home_primary_action_starts_with_tech_stack(self):
        home = self.api.get_work_home()

        self.assertEqual(home["primaryAction"]["type"], "create_tech_stack")
        self.assertEqual(home["summary"]["techStackCount"], 0)

    def test_tech_stack_detail_and_dynamic_resume_use_confirmed_evidence(self):
        stack = self.api.create_work_tech_stack(
            {
                "name": "RAG",
                "category": "AI Engineering",
                "proficiency": "practicing",
                "description": "Retrieval augmented generation systems.",
                "tags": ["retrieval", "knowledge"],
            }
        )
        project = self.api.create_work_project(
            {
                "title": "Universe Knowledge Provider",
                "description": "Connected Knowledge Service to RAGFlow through a provider adapter.",
                "techStackIds": [stack["id"]],
            }
        )
        resume = self.api.create_work_resume_draft({"roleTarget": "AI Engineer"})
        detail = self.api.get_work_tech_stack(stack["id"])
        home = self.api.get_work_home()

        self.assertEqual(detail["techStack"]["id"], stack["id"])
        self.assertEqual(detail["projects"][0]["id"], project["id"])
        self.assertIn("RAG", resume["content"])
        self.assertIn(f"tech_stack:{stack['id']}", resume["evidenceRefs"])
        self.assertIn(f"project:{project['id']}", resume["evidenceRefs"])
        self.assertEqual(home["primaryAction"]["type"], "review_resume")

    def test_work_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("GET", "/api/work/home"), contracts)
        self.assertIn(("POST", "/api/work/tech-stacks"), contracts)
        self.assertIn(("GET", "/api/work/tech-stacks/{tech_stack_id}"), contracts)
        self.assertIn(("POST", "/api/work/resumes/draft"), contracts)

    def test_work_frontend_routes_exist(self):
        router = (PROJECT_ROOT / "frontend/src/router/index.ts").read_text()
        portal = (PROJECT_ROOT / "frontend/src/universe/portal/UniversePortal.vue").read_text()

        self.assertIn("path: '/work'", router)
        self.assertIn("TechStackDirectory", router)
        self.assertIn("DynamicResume", router)
        self.assertIn("Enter Work Planet", portal)
        self.assertNotIn("/:futurePlanet(work|novel|life|creator)", router)


if __name__ == "__main__":
    unittest.main()
