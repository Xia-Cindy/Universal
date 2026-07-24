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

    def test_study_and_work_are_enterable_planets(self):
        planets = ApiFacade().list_planets()["planets"]
        enterable = [planet["name"] for planet in planets if planet["enterable"]]

        self.assertEqual(enterable, ["study", "work"])

    def test_universe_home_starfield_has_alternating_motion(self):
        styles = Path("frontend/src/styles.css").read_text()

        self.assertIn(".portal-shell::before", styles)
        self.assertIn(".portal-shell::after", styles)
        self.assertIn("animation: universe-stars-up", styles)
        self.assertIn("animation: universe-stars-down", styles)
        self.assertIn("@keyframes universe-stars-up", styles)
        self.assertIn("@keyframes universe-stars-down", styles)
        self.assertIn("@media (prefers-reduced-motion: reduce)", styles)


if __name__ == "__main__":
    unittest.main()
