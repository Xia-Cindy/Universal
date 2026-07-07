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

    return app


app = create_app()

