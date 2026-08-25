from backend.app.api.contracts import list_contracts
from backend.app.api.routes import api
from backend.app.core.settings import settings


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

    if settings.persistence_backend == "postgres" and not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is required for the default PostgreSQL runtime. "
            "Copy docker/universe.env.example, configure it, then load it before starting the API."
        )

    app = FastAPI(title="Universe OS API")

    @app.middleware("http")
    async def auth_context(request, call_next):
        token = request.headers.get("Authorization", "")
        token = token.removeprefix("Bearer ").strip() or None
        user = api.authenticate(token)
        context_token = api.users.set_current_user(user) if user else None
        try:
            return await call_next(request)
        finally:
            if context_token is not None:
                api.users.reset_current_user(context_token)

    @app.get("/api/health")
    def health():
        return api.health()

    @app.get("/api/ai/status")
    def ai_status():
        return api.ai_status()

    @app.post("/api/auth/register/request")
    def request_registration(payload: dict):
        return api.request_registration(payload)

    @app.post("/api/auth/register/verify")
    def verify_registration(payload: dict):
        return api.verify_registration(payload)

    @app.post("/api/auth/login")
    def login(payload: dict):
        return api.login(payload)

    @app.get("/api/auth/me")
    def auth_me():
        return api.current_auth_user()

    @app.get("/api/planets")
    def list_planets():
        return api.list_planets()

    @app.get("/api/planets/{planet_name}")
    def get_planet(planet_name: str):
        return api.get_planet(planet_name)

    @app.get("/api/study/home")
    def get_study_home():
        return api.get_study_home()

    @app.get("/api/work/home")
    def get_work_home():
        return api.get_work_home()

    @app.get("/api/work/cases")
    def list_work_cases():
        return api.list_work_cases()

    @app.post("/api/work/cases")
    def create_work_case(payload: dict):
        return api.create_work_case(payload)

    @app.get("/api/work/cases/{case_id}")
    def get_work_case(case_id: str):
        return api.get_work_case(case_id)

    @app.patch("/api/work/cases/{case_id}")
    def update_work_case(case_id: str, payload: dict):
        return api.update_work_case(case_id, payload)

    @app.get("/api/work/tech-stacks")
    def list_work_tech_stacks():
        return api.list_work_tech_stacks()

    @app.post("/api/work/tech-stacks")
    def create_work_tech_stack(payload: dict):
        return api.create_work_tech_stack(payload)

    @app.patch("/api/work/tech-stacks/{tech_stack_id}")
    def update_work_tech_stack(tech_stack_id: str, payload: dict):
        return api.update_work_tech_stack(tech_stack_id, payload)

    @app.delete("/api/work/tech-stacks/{tech_stack_id}")
    def delete_work_tech_stack(tech_stack_id: str):
        return api.delete_work_tech_stack(tech_stack_id)

    @app.get("/api/work/tech-stacks/{tech_stack_id}")
    def get_work_tech_stack(tech_stack_id: str):
        return api.get_work_tech_stack(tech_stack_id)

    @app.get("/api/work/tech-stacks/{tech_stack_id}/articles")
    def list_work_articles(tech_stack_id: str):
        return api.list_work_articles(tech_stack_id)

    @app.post("/api/work/tech-stacks/{tech_stack_id}/articles")
    def create_work_article(tech_stack_id: str, payload: dict):
        return api.create_work_article(tech_stack_id, payload)

    @app.post("/api/work/tech-stacks/{tech_stack_id}/explorations")
    def ask_work_exploration(tech_stack_id: str, payload: dict):
        return api.ask_work_exploration(tech_stack_id, payload)

    @app.get("/api/work/tech-stacks/{tech_stack_id}/learning-records")
    def list_work_learning_records(tech_stack_id: str):
        return api.list_work_learning_records(tech_stack_id)

    @app.post("/api/work/tech-stacks/{tech_stack_id}/learning-records")
    def create_work_learning_record(tech_stack_id: str, payload: dict):
        return api.create_work_learning_record(tech_stack_id, payload)

    @app.get("/api/work/community/csdn")
    def get_work_community_articles(topic: str = "java"):
        return api.get_work_community_articles(topic)

    @app.get("/api/work/community/csdn/article")
    def get_work_community_article_detail(url: str):
        return api.get_work_community_article_detail(url)

    @app.get("/api/work/projects")
    def list_work_projects():
        return api.list_work_projects()

    @app.post("/api/work/projects")
    def create_work_project(payload: dict):
        return api.create_work_project(payload)

    @app.get("/api/work/resumes")
    def list_work_resumes():
        return api.list_work_resumes()

    @app.post("/api/work/resumes/draft")
    def create_work_resume_draft(payload: dict):
        return api.create_work_resume_draft(payload)

    @app.get("/api/novel/drafts")
    def list_novel_drafts():
        return api.list_novel_drafts()

    @app.post("/api/novel/drafts")
    def create_novel_draft(payload: dict):
        return api.create_novel_draft(payload)

    @app.patch("/api/novel/drafts/{draft_id}")
    def update_novel_draft(draft_id: str, payload: dict):
        return api.update_novel_draft(draft_id, payload)

    @app.post("/api/work/knowledge/documents")
    def create_work_knowledge_document(payload: dict):
        return api.create_knowledge_document(payload)

    @app.get("/api/work/knowledge")
    def work_knowledge_overview():
        return api.work_knowledge_overview()

    @app.get("/api/work/knowledge/documents")
    def list_work_knowledge_documents(
        subject: str | None = None,
        topic: str | None = None,
        techStackId: str | None = None,
    ):
        return api.list_work_knowledge_documents(
            subject=subject,
            topic=topic,
            tech_stack_id=techStackId,
        )

    @app.get("/api/work/knowledge/documents/{document_id}")
    def get_work_knowledge_document(document_id: str):
        return api.get_work_knowledge_document(document_id)

    @app.get("/api/study/knowledge/documents/{document_id}/share-grants")
    def list_knowledge_share_grants(document_id: str):
        return api.list_knowledge_share_grants(document_id)

    @app.post("/api/study/knowledge/documents/{document_id}/share-grants")
    def create_knowledge_share_grant(document_id: str, payload: dict):
        return api.create_knowledge_share_grant(document_id, payload)

    @app.get("/api/study/knowledge/documents/{document_id}/goal-links")
    def get_knowledge_document_goal_links(document_id: str):
        return api.get_knowledge_document_goal_links(document_id)

    @app.put("/api/study/knowledge/documents/{document_id}/goal-links")
    def replace_knowledge_document_goal_links(document_id: str, payload: dict):
        return api.replace_knowledge_document_goal_links(document_id, payload)

    @app.get("/api/study/knowledge/documents/{document_id}/reading-progress")
    def get_knowledge_reading_progress(document_id: str):
        return api.get_knowledge_reading_progress(document_id)

    @app.put("/api/study/knowledge/documents/{document_id}/reading-progress")
    def save_knowledge_reading_progress(document_id: str, payload: dict):
        return api.save_knowledge_reading_progress(document_id, payload)

    @app.delete("/api/study/knowledge/share-grants/{grant_id}")
    def revoke_knowledge_share_grant(grant_id: str):
        return api.revoke_knowledge_share_grant(grant_id)

    @app.post("/api/work/knowledge/documents/{document_id}/process")
    def process_work_knowledge_document(document_id: str):
        return api.process_work_knowledge_document(document_id)

    @app.get("/api/work/knowledge/documents/{document_id}/status")
    def refresh_work_knowledge_document(document_id: str):
        return api.refresh_work_knowledge_document(document_id)

    @app.get("/api/study/workspace")
    def get_study_workspace():
        return api.get_study_workspace()

    @app.get("/api/study/onboarding")
    def get_study_onboarding():
        return api.get_study_onboarding()

    @app.post("/api/study/onboarding/goal")
    def create_onboarding_goal(payload: dict):
        return api.create_onboarding_goal(payload)

    @app.post("/api/study/goals")
    def create_goal(payload: dict):
        return api.create_goal(payload)

    @app.get("/api/study/goals")
    def list_goals():
        return api.list_goals()

    @app.patch("/api/study/goals/{goal_id}")
    def update_goal(goal_id: str, payload: dict):
        return api.update_goal(goal_id, payload)

    @app.post("/api/study/goals/{goal_id}/switch")
    def switch_goal(goal_id: str):
        return api.switch_goal(goal_id)

    @app.get("/api/study/goals/active")
    def get_active_goal():
        return api.get_active_goal()

    @app.post("/api/study/plans")
    def create_plan(payload: dict | None = None):
        return api.create_plan(payload)

    @app.post("/api/study/plans/nodes")
    def create_plan_node(payload: dict):
        return api.create_plan_node(payload)

    @app.get("/api/study/plans/current")
    def get_current_plan():
        return api.get_current_plan()

    @app.patch("/api/study/plans/year/{plan_id}")
    def update_year_plan(plan_id: str, payload: dict):
        return api.update_year_plan(plan_id, payload)

    @app.patch("/api/study/plans/month/{plan_id}")
    def update_month_plan(plan_id: str, payload: dict):
        return api.update_month_plan(plan_id, payload)

    @app.patch("/api/study/plans/week/{plan_id}")
    def update_week_plan(plan_id: str, payload: dict):
        return api.update_week_plan(plan_id, payload)

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

    @app.get("/api/study/wordbook/entries")
    def list_wordbook_entries(goalId: str | None = None, language: str | None = None, tag: str | None = None):
        return api.list_wordbook_entries(goal_id=goalId, language=language, tag=tag)

    @app.post("/api/study/wordbook/entries")
    def create_wordbook_entry(payload: dict):
        return api.create_wordbook_entry(payload)

    @app.get("/api/study/wordbook/entries/{entry_id}")
    def get_wordbook_entry(entry_id: str):
        return api.get_wordbook_entry(entry_id)

    @app.patch("/api/study/wordbook/entries/{entry_id}")
    def update_wordbook_entry(entry_id: str, payload: dict):
        return api.update_wordbook_entry(entry_id, payload)

    @app.delete("/api/study/wordbook/entries/{entry_id}")
    def delete_wordbook_entry(entry_id: str):
        return api.delete_wordbook_entry(entry_id)

    @app.post("/api/study/wordbook/import")
    def import_wordbook_entries(payload: dict):
        return api.import_wordbook_entries(payload)

    @app.post("/api/study/wordbook/entries/{entry_id}/dictionary/refresh")
    def refresh_wordbook_dictionary(entry_id: str):
        return api.refresh_wordbook_dictionary(entry_id)

    @app.post("/api/study/wordbook/entries/{entry_id}/review")
    def review_wordbook_entry(entry_id: str, payload: dict):
        return api.review_wordbook_entry(entry_id, payload)

    @app.get("/api/study/recall/schedules")
    def list_recall_schedules(goalId: str | None = None):
        return api.list_recall_schedules(goal_id=goalId)

    @app.get("/api/study/recall/schedules/{source_type}/{source_id}")
    def get_recall_schedule(source_type: str, source_id: str):
        return api.get_recall_schedule(source_type, source_id)

    @app.patch("/api/study/recall/schedules/{source_type}/{source_id}")
    def adjust_recall_schedule(source_type: str, source_id: str, payload: dict):
        return api.adjust_recall_schedule(source_type, source_id, payload)

    @app.post("/api/study/tutor/events")
    def save_tutor_answer_event(payload: dict):
        return api.save_tutor_answer_event(payload)

    @app.post("/api/study/knowledge/documents")
    def create_knowledge_document(payload: dict):
        return api.create_knowledge_document(payload)

    @app.post("/api/study/knowledge/documents/adopt-ragflow")
    def adopt_ragflow_knowledge_document(payload: dict):
        return api.adopt_ragflow_knowledge_document(payload)

    @app.get("/api/study/knowledge")
    def knowledge_overview():
        return api.knowledge_overview()

    @app.get("/api/study/knowledge/documents")
    def list_knowledge_documents(
        subject: str | None = None,
        topic: str | None = None,
        goalId: str | None = None,
        planetType: str | None = None,
        techStackId: str | None = None,
    ):
        return api.list_study_knowledge_documents(
            subject=subject,
            topic=topic,
            goal_id=goalId,
            planet_type=planetType,
            tech_stack_id=techStackId,
        )

    @app.get("/api/study/knowledge/documents/{document_id}")
    def get_knowledge_document(document_id: str):
        return api.get_knowledge_document(document_id)

    @app.get("/api/study/knowledge/documents/{document_id}/annotations")
    def list_knowledge_annotations(document_id: str):
        return api.list_knowledge_annotations(document_id)

    @app.post("/api/study/knowledge/documents/{document_id}/annotations")
    def create_knowledge_annotation(document_id: str, payload: dict):
        return api.create_knowledge_annotation(document_id, payload)

    @app.patch("/api/study/knowledge/documents/{document_id}/annotations/{annotation_id}")
    def update_knowledge_annotation(document_id: str, annotation_id: str, payload: dict):
        return api.update_knowledge_annotation(document_id, annotation_id, payload)

    @app.post("/api/study/knowledge/documents/{document_id}/annotations/{annotation_id}/mastered")
    def mark_knowledge_annotation_mastered(document_id: str, annotation_id: str, payload: dict):
        return api.mark_knowledge_annotation_mastered(document_id, annotation_id, payload)

    @app.delete("/api/study/knowledge/documents/{document_id}/annotations/{annotation_id}")
    def delete_knowledge_annotation(document_id: str, annotation_id: str):
        return api.delete_knowledge_annotation(document_id, annotation_id)

    @app.get("/api/study/knowledge/documents/{document_id}/evidence")
    def get_knowledge_evidence(document_id: str):
        return api.get_knowledge_evidence(document_id)

    @app.get("/api/study/knowledge/documents/{document_id}/status")
    def refresh_knowledge_document(document_id: str):
        return api.refresh_knowledge_document(document_id)

    @app.post("/api/study/knowledge/documents/{document_id}/process")
    def process_knowledge_document(document_id: str):
        return api.process_knowledge_document(document_id)

    @app.post("/api/study/knowledge/documents/{document_id}/retry")
    def retry_knowledge_document(document_id: str):
        return api.retry_knowledge_document(document_id)

    @app.delete("/api/study/knowledge/documents/{document_id}")
    def delete_knowledge_document(document_id: str):
        return api.delete_knowledge_document(document_id)

    @app.get("/api/knowledge/provider/health")
    def knowledge_provider_health():
        return api.knowledge_provider_health()

    @app.post("/api/knowledge/provider/runtime-verification")
    def verify_knowledge_provider_runtime():
        return api.verify_knowledge_provider_runtime()

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

    @app.get("/api/study/feedback/recommendations")
    def get_study_feedback_recommendations():
        return api.get_study_feedback_recommendations()

    @app.post("/api/study/review/wrong-questions")
    def create_wrong_question(payload: dict):
        return api.create_wrong_question(payload)

    @app.get("/api/study/review/wrong-questions")
    def list_wrong_questions():
        return api.list_wrong_questions()

    @app.get("/api/study/review/queue")
    def get_review_queue(includeFuture: bool = False):
        return api.get_review_queue(include_future=includeFuture)

    @app.post("/api/study/review/items/{review_id}/complete")
    def complete_review_item(review_id: str, payload: dict | None = None):
        return api.complete_review_item(review_id, payload)

    return app


app = create_app()
