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

    @app.get("/api/study/onboarding")
    def get_study_onboarding():
        return api.get_study_onboarding()

    @app.post("/api/study/onboarding/goal")
    def create_onboarding_goal(payload: dict):
        return api.create_onboarding_goal(payload)

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

    @app.post("/api/study/execution/sessions")
    def start_execution_session(payload: dict):
        return api.start_execution_session(payload)

    @app.patch("/api/study/execution/sessions/{session_id}/finish")
    def finish_execution_session(session_id: str, payload: dict | None = None):
        return api.finish_execution_session(session_id, payload)

    @app.get("/api/study/records")
    def list_study_records():
        return api.list_study_records()

    @app.post("/api/study/tutor/ask")
    def ask_study_tutor(payload: dict):
        return api.ask_study_tutor(payload)

    @app.get("/api/study/tutor/history")
    def get_tutor_history():
        return api.get_tutor_history()

    @app.post("/api/study/knowledge/documents")
    def create_knowledge_document(payload: dict):
        return api.create_knowledge_document(payload)

    @app.get("/api/study/knowledge")
    def knowledge_overview():
        return api.knowledge_overview()

    @app.get("/api/study/knowledge/documents")
    def list_knowledge_documents(subject: str | None = None, topic: str | None = None):
        return api.list_knowledge_documents(subject=subject, topic=topic)

    @app.get("/api/study/knowledge/documents/{document_id}")
    def get_knowledge_document(document_id: str):
        return api.get_knowledge_document(document_id)

    @app.post("/api/study/knowledge/documents/{document_id}/process")
    def process_knowledge_document(document_id: str):
        return api.process_knowledge_document(document_id)

    @app.patch("/api/study/knowledge/documents/{document_id}")
    def update_knowledge_document(document_id: str, payload: dict):
        return api.update_knowledge_document(document_id, payload)

    @app.post("/api/study/knowledge/documents/{document_id}/embeddings/prepare")
    def prepare_document_embeddings(document_id: str):
        return api.prepare_document_embeddings(document_id)

    @app.get("/api/study/knowledge/documents/{document_id}/embeddings")
    def list_document_embeddings(document_id: str):
        return api.list_document_embeddings(document_id)

    @app.post("/api/study/knowledge/retrieval/search")
    def search_knowledge_chunks(payload: dict):
        return api.search_knowledge_chunks(payload)

    @app.post("/api/memory")
    def create_memory(payload: dict):
        return api.create_memory(payload)

    @app.get("/api/memory")
    def list_memory(
        scope: str | None = None,
        planetType: str | None = None,
        sessionId: str | None = None,
        key: str | None = None,
        includeInactive: bool = True,
    ):
        return api.list_memory(
            scope=scope,
            planet_type=planetType,
            session_id=sessionId,
            key=key,
            include_inactive=includeInactive,
        )

    @app.patch("/api/memory/{memory_id}")
    def update_memory(memory_id: str, payload: dict):
        return api.update_memory(memory_id, payload)

    @app.post("/api/memory/{memory_id}/archive")
    def archive_memory(memory_id: str):
        return api.archive_memory(memory_id)

    @app.get("/api/memory/context")
    def memory_context(planetType: str | None = None, sessionId: str | None = None):
        return api.memory_context(planet_type=planetType, session_id=sessionId)

    @app.get("/api/study/analytics")
    def get_study_analytics():
        return api.get_study_analytics()

    @app.post("/api/study/analytics/report")
    def create_study_analytics_report():
        return api.create_study_analytics_report()

    return app


app = create_app()
