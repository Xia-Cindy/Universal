from backend.app.planet_engine import PlanetRegistry


class UniverseService:
    def __init__(self, planet_registry: PlanetRegistry) -> None:
        self._planet_registry = planet_registry

    def portal(self) -> dict[str, object]:
        payload = self._planet_registry.portal_payload()
        payload["experience"] = "personal_intelligent_world"
        return payload

    def planet(self, name: str) -> dict[str, object]:
        return self._planet_registry.get_planet(name).to_dict()

