import unittest
from pathlib import Path


class SpatialRouteSmokeContractTests(unittest.TestCase):
    def test_smoke_script_covers_the_normal_entry_and_core_routes(self):
        source = Path("scripts/smoke_spatial_routes.py").read_text()

        for route in (
            '"/"',
            '"/study"',
            '"/study/plan"',
            '"/study/knowledge"',
            '"/study/wordbook"',
            '"/study/cards"',
            '"/work"',
            '"/novel"',
        ):
            self.assertIn(route, source)
        self.assertIn('"/api/health"', source)
        self.assertIn('id="root"', source)

    def test_room_route_configuration_keeps_the_normal_entry_contract(self):
        vite_config = Path("room-portfolio/vite.config.js").read_text()
        spaces = Path("room-portfolio/src/spaces.js").read_text()

        self.assertIn("port: 5180", vite_config)
        self.assertIn("'/api': 'http://127.0.0.1:8000'", vite_config)
        for route in ("/study", "/study/knowledge", "/study/wordbook", "/study/cards", "/work", "/novel"):
            self.assertIn(f"path: '{route}'", spaces)


if __name__ == "__main__":
    unittest.main()
