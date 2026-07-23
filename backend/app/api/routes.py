from backend.app.ai import AICoreService, AgentDefinition, DefaultToolRouter
from backend.app.core.settings import settings
from backend.app.knowledge import KnowledgeRepository, KnowledgeService
from backend.app.knowledge.providers import RAGFlowClient, RAGFlowKnowledgeProvider
from backend.app.memory import MemoryService
from backend.app.models import MemoryScope
from backend.app.planet_engine import create_default_registry
from backend.app.planets.study.analytics import StudyAnalystContextProvider, StudyAnalyticsService
from backend.app.planets.study.dashboard import StudyHomeService
from backend.app.planets.study.execution import StudyExecutionService
from backend.app.planets.study.goals import GoalService
from backend.app.planets.study.onboarding import StudyOnboardingService
from backend.app.planets.study.plans import PlanService
from backend.app.planets.study.repository import StudyRepository
from backend.app.planets.study.sessions import SessionService
from backend.app.planets.study.tutor import TutorService
from backend.app.planets.study.tutor.context_provider import StudyTutorContextProvider
from backend.app.planets.study.workspace import StudyWorkspaceService
from backend.app.planets.work import WorkRepository, WorkService
from backend.app.retrieval import RetrievalQuery, RetrievalService, RetrieverTool
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
        self.knowledge_repository = KnowledgeRepository()
        self.knowledge_provider = self._create_knowledge_provider()
        self.knowledge = KnowledgeService(
            repository=self.knowledge_repository,
            provider=self.knowledge_provider,
        )
        self.retrieval = RetrievalService(
            knowledge_repository=self.knowledge_repository,
            knowledge_provider=self.knowledge_provider,
        )
        self.tool_router = DefaultToolRouter()
        self.tool_router.register(RetrieverTool(self.retrieval))
        self.ai_core = AICoreService(tool_router=self.tool_router)
        self.ai_core.agent_manager.register(
            AgentDefinition(
                agent_id="study",
                capabilities=("tutor",),
                prompt_key="study.tutor.answer",
                context_builder="study.tutor",
                allowed_tools=("retrieval.search",),
            )
        )
        self.ai_core.agent_manager.register(
            AgentDefinition(
                agent_id="study",
                capabilities=("analyst",),
                prompt_key="study.analyst.report",
                context_builder="study.analyst",
                allowed_tools=("retrieval.search",),
            )
        )
        self.ai_core.prompt_manager.register(
            "study.tutor.answer",
            (
                "You are the Study Agent Tutor capability. Use Study workflow context and optional "
                "retrieved Knowledge chunks when provided. Do not generate citations or invent sources."
            ),
        )
        self.ai_core.prompt_manager.register(
            "study.analyst.report",
            (
                "You are the Study Agent Analyst capability. Explain Study progress, patterns, "
                "and next actions from provided data. Do not make autonomous decisions or infer personality."
            ),
        )
        self.ai_core.context_manager.register_provider(
            "study.tutor",
            StudyTutorContextProvider(),
        )
        self.ai_core.context_manager.register_provider(
            "study.analyst",
            StudyAnalystContextProvider(),
        )
        self.study_goals = GoalService(self.study_repository, self.memory)
        self.study_onboarding = StudyOnboardingService(
            goals=self.study_goals,
            memory=self.memory,
        )
        self.study_plans = PlanService(self.study_repository)
        self.study_sessions = SessionService(self.study_repository)
        self.study_execution = StudyExecutionService(
            repository=self.study_repository,
            sessions=self.study_sessions,
            memory=self.memory,
        )
        self.study_tutor = TutorService(
            repository=self.study_repository,
            ai_core=self.ai_core,
        )
        self.study_home = StudyHomeService(self.study_repository)
        self.study_workspace = StudyWorkspaceService(self.study_repository)
        self.study_analytics = StudyAnalyticsService(
            repository=self.study_repository,
            ai_core=self.ai_core,
        )
        self.work_repository = WorkRepository()
        self.work = WorkService(self.work_repository)

    def _create_knowledge_provider(self):
        if settings.knowledge_provider != "ragflow":
            return None
        if not settings.ragflow_api_key:
            raise ValueError("RAGFLOW_API_KEY is required when KNOWLEDGE_PROVIDER=ragflow")
        return RAGFlowKnowledgeProvider(
            client=RAGFlowClient(
                base_url=settings.ragflow_base_url,
                api_key=settings.ragflow_api_key,
            ),
            dataset_id=settings.ragflow_dataset_id or None,
            dataset_name=settings.ragflow_dataset_name,
        )

    def health(self) -> dict[str, str]:
        return {"status": "ok", "product": settings.app_name}

    def list_planets(self) -> dict[str, object]:
        return self.universe.portal()

    def get_planet(self, planet_name: str) -> dict[str, object]:
        return self.universe.planet(planet_name)

    def get_work_home(self) -> dict[str, object]:
        user = self.users.current_user()
        self.registry.get_enterable_planet("work")
        return self.work.home(
            user.id,
            knowledge_summary=self.knowledge.overview(user.id),
        )

    def list_work_tech_stacks(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.work.list_tech_stacks(user.id)

    def create_work_tech_stack(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.create_tech_stack(user.id, payload)

    def get_work_tech_stack(self, tech_stack_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.tech_stack_detail(
            user.id,
            tech_stack_id,
            knowledge_summary=self.knowledge.overview(user.id),
        )

    def list_work_projects(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.work.list_projects(user.id)

    def create_work_project(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.create_project(user.id, payload)

    def list_work_resumes(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.work.list_resumes(user.id)

    def create_work_resume_draft(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.create_resume_draft(user.id, payload)

    def get_study_home(self) -> dict[str, object]:
        user = self.users.current_user()
        planet = self.registry.get_enterable_planet("study")
        memory_context = self.memory.prepare_context(user.id, planet_type="study")
        analytics = self.study_analytics.analytics(user=user, memory_context=memory_context)
        return self.study_home.home(
            user=user,
            planet=planet,
            ai_insight={
                "learningInsights": analytics["learningInsights"],
                "recommendedActions": analytics["recommendedActions"],
                "dataQuality": analytics["dataQuality"],
            },
            knowledge_status=self.knowledge.overview(user.id),
        )

    def get_study_workspace(self) -> dict[str, object]:
        user = self.users.current_user()
        planet = self.registry.get_enterable_planet("study")
        memory_context = self.memory.prepare_context(user.id, planet_type="study")
        analytics = self.study_analytics.analytics(user=user, memory_context=memory_context)
        return self.study_workspace.workspace(
            user=user,
            planet=planet,
            knowledge_summary=self.knowledge.overview(user.id),
            analytics_summary=analytics,
        )

    def get_study_onboarding(self) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_onboarding.status(user.id)

    def create_onboarding_goal(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_onboarding.create_goal(user.id, payload)

    def create_goal(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_goals.create_goal(user.id, payload).to_dict()

    def list_goals(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return [goal.to_dict() for goal in self.study_goals.list_goals(user.id)]

    def update_goal(self, goal_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_goals.update_goal(user.id, goal_id, payload).to_dict()

    def switch_goal(self, goal_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_goals.switch_goal(user.id, goal_id).to_dict()

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

    def update_year_plan(self, plan_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_plans.update_year_plan(user.id, plan_id, payload).to_dict()

    def update_month_plan(self, plan_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_plans.update_month_plan(user.id, plan_id, payload).to_dict()

    def update_week_plan(self, plan_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_plans.update_week_plan(user.id, plan_id, payload).to_dict()

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

    def start_execution_session(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_execution.start(user.id, payload)

    def finish_execution_session(
        self,
        session_id: str,
        payload: dict | None = None,
    ) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_execution.finish(user.id, session_id, payload)

    def list_study_records(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return [session.to_dict() for session in self.study_sessions.list_records(user.id)]

    def ask_study_tutor(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        memory_context = self.memory.prepare_context(
            user.id,
            planet_type="study",
            session_id=payload.get("sessionId"),
        )
        return self.study_tutor.ask(
            user=user,
            question=payload["question"],
            memory_context=memory_context,
        )

    def get_tutor_history(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.study_tutor.history(user=user)

    def create_knowledge_document(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        if payload.get("goalId"):
            self.study_repository.get_goal(payload["goalId"], user.id)
        return self.knowledge.create_document(user.id, payload).to_dict()

    def knowledge_overview(self) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.overview(user.id)

    def list_knowledge_documents(
        self,
        *,
        subject: str | None = None,
        topic: str | None = None,
        goal_id: str | None = None,
    ) -> list[dict[str, object]]:
        user = self.users.current_user()
        if goal_id:
            self.study_repository.get_goal(goal_id, user.id)
        return self.knowledge.list_documents(
            user.id,
            subject=subject,
            topic=topic,
            goal_id=goal_id,
        )

    def get_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.document_detail(user.id, document_id)

    def process_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.process_document(user.id, document_id)

    def update_knowledge_document(self, document_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.update_document(user.id, document_id, payload).to_dict()

    def prepare_document_embeddings(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.retrieval.prepare_document_embeddings(user.id, document_id)

    def list_document_embeddings(self, document_id: str) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.retrieval.list_document_embeddings(user.id, document_id)

    def search_knowledge_chunks(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.retrieval.search(
            RetrievalQuery(
                user_id=user.id,
                query=payload["query"],
                limit=payload.get("limit", 5),
                document_id=payload.get("documentId"),
            )
        )

    def create_memory(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.memory.create_from_payload(user.id, payload).to_dict()

    def list_memory(
        self,
        *,
        scope: str | None = None,
        planet_type: str | None = None,
        session_id: str | None = None,
        key: str | None = None,
        include_inactive: bool = True,
    ) -> list[dict[str, object]]:
        user = self.users.current_user()
        entries = self.memory.list_for_user(
            user.id,
            scope=MemoryScope(scope) if scope else None,
            planet_type=planet_type,
            session_id=session_id,
            key=key,
            include_inactive=include_inactive,
            mark_accessed=True,
        )
        return [entry.to_dict() for entry in entries]

    def update_memory(self, memory_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.memory.update(user.id, memory_id, payload).to_dict()

    def archive_memory(self, memory_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.memory.archive(user.id, memory_id).to_dict()

    def memory_context(
        self,
        *,
        planet_type: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, object]:
        user = self.users.current_user()
        return self.memory.prepare_context(
            user.id,
            planet_type=planet_type,
            session_id=session_id,
        )

    def get_study_analytics(self) -> dict[str, object]:
        user = self.users.current_user()
        memory_context = self.memory.prepare_context(user.id, planet_type="study")
        return self.study_analytics.analytics(
            user=user,
            memory_context=memory_context,
        )

    def create_study_analytics_report(self) -> dict[str, object]:
        user = self.users.current_user()
        memory_context = self.memory.prepare_context(user.id, planet_type="study")
        return self.study_analytics.report(
            user=user,
            memory_context=memory_context,
        )


api = ApiFacade()
