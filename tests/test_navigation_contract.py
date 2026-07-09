import unittest
from pathlib import Path

from backend.app.api.routes import ApiFacade


class NavigationContractTests(unittest.TestCase):
    def test_study_workspace_can_return_to_universe(self):
        layout = Path("frontend/src/planets/study/layout/StudyWorkspace.vue").read_text()

        self.assertIn('to="/">Universe Home</RouterLink>', layout)
        self.assertIn("Universe / Study Planet", layout)

    def test_study_workspace_navigation_keeps_expected_modules(self):
        layout = Path("frontend/src/planets/study/layout/StudyWorkspace.vue").read_text()

        for label in ("Home", "Plan", "Knowledge", "Tutor", "Review", "Analytics"):
            self.assertIn(f"label: '{label}'", layout)

    def test_study_planet_remains_only_enterable_planet(self):
        planets = ApiFacade().list_planets()["planets"]
        enterable = [planet["name"] for planet in planets if planet["enterable"]]

        self.assertEqual(enterable, ["study"])


if __name__ == "__main__":
    unittest.main()
