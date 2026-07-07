from backend.app.core.settings import settings
from backend.app.memory import MemoryService
from backend.app.planet_engine import create_default_registry
from backend.app.planets.study.dashboard import StudyHomeService
from backend.app.planets.study.goals import GoalService
from backend.app.planets.study.plans import PlanService
from backend.app.planets.study.repository import StudyRepository
from backend.app.planets.study.sessions import SessionService
from backend.app.universe import UniverseService
from backend.app.users import UserService


class ApiFacade:
    """Dependency-light API facade used by tests and optional web adapters."""

    def __init__(self) -> None:
        self.registry = create_default_registry()
        self.universe = UniverseService(self.registry)
        self.users = UserService(settings.default_user_id)
        self.memory = MemoryService()
        self.study_repository = StudyRepository()
        self.study_goals = GoalService(self.study_repository, self.memory)
        self.study_plans = PlanService(self.study_repository)
        self.study_sessions = SessionService(self.study_repository)
        self.study_home = StudyHomeService(self.study_repository)

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

    def create_goal(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_goals.create_goal(user.id, payload).to_dict()

    def update_goal(self, goal_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_goals.update_goal(user.id, goal_id, payload).to_dict()

    def get_active_goal(self) -> dict[str, object] | None:
        user = self.users.current_user()
        goal = self.study_goals.get_active_goal(user.id)
        return goal.to_dict() if goal else None

    def create_plan(self, payload: dict | None = None) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_plans.create_plan(user.id, payload)

    def get_current_plan(self) -> dict[str, object] | None:
        user = self.users.current_user()
        return self.study_plans.get_current_plan(user.id)

    def update_task(self, task_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_plans.update_task(user.id, task_id, payload).to_dict()

    def complete_task(self, task_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_plans.complete_task(user.id, task_id).to_dict()

    def start_session(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_sessions.start_session(user.id, payload).to_dict()

    def finish_session(self, session_id: str, payload: dict | None = None) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_sessions.finish_session(user.id, session_id, payload).to_dict()

    def list_study_records(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return [session.to_dict() for session in self.study_sessions.list_records(user.id)]


api = ApiFacade()
