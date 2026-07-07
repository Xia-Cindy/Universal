from backend.app.api.contracts import list_contracts
from backend.app.api.routes import api


def create_app():
    """Create the web app when FastAPI is installed.

    Milestone 1 keeps the core API contract dependency-light. Installing and
    running FastAPI is part of the runtime setup, while service tests can run
    with the Python standard library.
    """

    try:
        from fastapi import FastAPI
    except ModuleNotFoundError:
        return {
            "app": "Universe OS API",
            "status": "fastapi_not_installed",
            "contracts": list_contracts(),
        }

    app = FastAPI(title="Universe OS API")

    @app.get("/api/health")
    def health():
        return api.health()

    @app.get("/api/planets")
    def list_planets():
        return api.list_planets()

    @app.get("/api/planets/{planet_name}")
    def get_planet(planet_name: str):
        return api.get_planet(planet_name)

    @app.get("/api/study/home")
    def get_study_home():
        return api.get_study_home()

    @app.post("/api/study/goals")
    def create_goal(payload: dict):
        return api.create_goal(payload)

    @app.patch("/api/study/goals/{goal_id}")
    def update_goal(goal_id: str, payload: dict):
        return api.update_goal(goal_id, payload)

    @app.get("/api/study/goals/active")
    def get_active_goal():
        return api.get_active_goal()

    @app.post("/api/study/plans")
    def create_plan(payload: dict | None = None):
        return api.create_plan(payload)

    @app.get("/api/study/plans/current")
    def get_current_plan():
        return api.get_current_plan()

    @app.patch("/api/study/tasks/{task_id}")
    def update_task(task_id: str, payload: dict):
        return api.update_task(task_id, payload)

    @app.patch("/api/study/tasks/{task_id}/complete")
    def complete_task(task_id: str):
        return api.complete_task(task_id)

    @app.post("/api/study/sessions")
    def start_session(payload: dict):
        return api.start_session(payload)

    @app.patch("/api/study/sessions/{session_id}/finish")
    def finish_session(session_id: str, payload: dict | None = None):
        return api.finish_session(session_id, payload)

    @app.get("/api/study/records")
    def list_study_records():
        return api.list_study_records()

    return app


app = create_app()
