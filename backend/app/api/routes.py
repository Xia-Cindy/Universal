from backend.app.core.settings import settings
from backend.app.planet_engine import create_default_registry
from backend.app.planets.study.dashboard import StudyHomeService
from backend.app.universe import UniverseService
from backend.app.users import UserService


class ApiFacade:
    """Dependency-light API facade used by tests and optional web adapters."""

    def __init__(self) -> None:
        self.registry = create_default_registry()
        self.universe = UniverseService(self.registry)
        self.users = UserService(settings.default_user_id)
        self.study_home = StudyHomeService()

    def health(self) -> dict[str, str]:
        return {"status": "ok", "product": settings.app_name}

    def list_planets(self) -> dict[str, object]:
        return self.universe.portal()

    def get_planet(self, planet_name: str) -> dict[str, object]:
        return self.universe.planet(planet_name)

    def get_study_home(self) -> dict[str, object]:
        user = self.users.current_user()
        planet = self.registry.get_enterable_planet("study")
        return self.study_home.home(user=user, planet=planet)


api = ApiFacade()

