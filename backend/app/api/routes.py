from backend.app.ai import AICoreService, AgentDefinition, DefaultToolRouter
from backend.app.core.dates import local_today
from backend.app.core.settings import settings
from backend.app.knowledge import (
    EnglishDictionaryService,
    FallbackEnglishDictionaryProvider,
    FreeDictionaryProvider,
    KnowledgeRepository,
    KnowledgeService,
    StaticEnglishDictionaryProvider,
)
from backend.app.knowledge.repository import SQLiteKnowledgeRepository
from backend.app.knowledge.providers import RAGFlowClient, RAGFlowKnowledgeProvider
from backend.app.memory import MemoryService
from backend.app.memory.repository import SQLiteMemoryRepository
from backend.app.models import LearningEvent, MemoryScope, RecallSourceType
from backend.app.planet_engine import create_default_registry
from backend.app.planets.study.analytics import StudyAnalystContextProvider, StudyAnalyticsService
from backend.app.planets.study.dashboard import StudyHomeService
from backend.app.planets.study.execution import StudyExecutionService
from backend.app.planets.study.goals import GoalService
from backend.app.planets.study.onboarding import StudyOnboardingService
from backend.app.planets.study.plans import PlanService
from backend.app.planets.study.repository import SQLiteStudyRepository, StudyRepository
from backend.app.planets.study.sessions import SessionService
from backend.app.planets.study.tutor import TutorService
from backend.app.planets.study.tutor.context_provider import StudyTutorContextProvider
from backend.app.planets.study.workspace import StudyWorkspaceService
from backend.app.planets.study.review import ReviewService
from backend.app.planets.study.recall import StudyRecallService
from backend.app.planets.study.wordbook import WordbookService
from backend.app.planets.work import CSDNCommunityService, WorkRepository, WorkService
from backend.app.planets.work.repository import SQLiteWorkRepository
from backend.app.planets.novel import NovelDraftService, NovelRepository, SQLiteNovelRepository
from backend.app.persistence import (
    PostgresKnowledgeRepository,
    PostgresMemoryRepository,
    PostgresNovelRepository,
    PostgresPersistence,
    PostgresStudyRepository,
    PostgresWorkRepository,
    SQLitePersistence,
)
from backend.app.storage import LocalObjectStorage, S3ObjectStorage
from backend.app.retrieval import RetrievalQuery, RetrievalService, RetrieverTool
from backend.app.universe import UniverseService
from backend.app.users import AuthService, ConsoleEmailSender, SMTPEmailSender, UserService


class ApiFacade:
    """Dependency-light API facade used by tests and optional web adapters."""

    def __init__(
        self,
        *,
        database_path: str | None = None,
        persistence_backend: str | None = None,
        database_url: str | None = None,
        english_dictionary_provider=None,
    ) -> None:
        self.registry = create_default_registry()
        self.universe = UniverseService(self.registry)
        backend = persistence_backend or ("sqlite" if database_path else "memory")
        if backend == "postgres":
            database_url = database_url or settings.database_url
            if not database_url:
                raise ValueError("DATABASE_URL is required when PERSISTENCE_BACKEND=postgres")
            self.persistence = PostgresPersistence(database_url)
            study_repository = PostgresStudyRepository(self.persistence)
            knowledge_repository = PostgresKnowledgeRepository(self.persistence)
            memory_repository = PostgresMemoryRepository(self.persistence)
            novel_repository = PostgresNovelRepository(self.persistence)
            work_repository = PostgresWorkRepository(self.persistence)
        elif backend == "sqlite":
            self.persistence = SQLitePersistence(database_path) if database_path else None
            study_repository = SQLiteStudyRepository(self.persistence) if self.persistence else StudyRepository()
            knowledge_repository = SQLiteKnowledgeRepository(self.persistence) if self.persistence else KnowledgeRepository()
            memory_repository = SQLiteMemoryRepository(self.persistence) if self.persistence else None
            novel_repository = SQLiteNovelRepository(self.persistence) if self.persistence else NovelRepository()
            work_repository = SQLiteWorkRepository(self.persistence) if self.persistence else WorkRepository()
        elif backend == "memory":
            self.persistence = None
            study_repository = StudyRepository()
            knowledge_repository = KnowledgeRepository()
            memory_repository = None
            novel_repository = NovelRepository()
            work_repository = WorkRepository()
        else:
            raise ValueError("PERSISTENCE_BACKEND must be postgres, sqlite, or memory")
        self.users = UserService(settings.default_user_id, persistence=self.persistence)
        email_sender = (
            SMTPEmailSender(
                host=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                sender=settings.smtp_from,
            )
            if settings.email_backend == "smtp"
            else ConsoleEmailSender()
        )
        self.auth = AuthService(users=self.users, persistence=self.persistence, sender=email_sender)
        self.memory = MemoryService(
            repository=memory_repository,
        )
        self.study_repository = study_repository
        self.knowledge_repository = knowledge_repository
        self.object_storage = self._create_object_storage()
        self.knowledge_provider = self._create_knowledge_provider()
        self.knowledge = KnowledgeService(
            repository=self.knowledge_repository,
            provider=self.knowledge_provider,
            storage=self.object_storage,
        )
        self.english_dictionary = EnglishDictionaryService(
            repository=self.knowledge_repository,
            provider=english_dictionary_provider or self._create_english_dictionary_provider(backend),
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
        self.study_review = ReviewService(self.study_repository)
        self.study_wordbook = WordbookService(
            self.study_repository,
            dictionary=self.english_dictionary,
        )
        self.study_recall = StudyRecallService(self.study_repository, self.knowledge)
        self.study_tutor = TutorService(
            repository=self.study_repository,
            ai_core=self.ai_core,
        )
        self.study_home = StudyHomeService(self.study_repository)
        self.study_workspace = StudyWorkspaceService(self.study_repository)
        self.study_analytics = StudyAnalyticsService(
            repository=self.study_repository,
            ai_core=self.ai_core,
            review=self.study_review,
            knowledge_repository=self.knowledge_repository,
        )
        self.work_repository = work_repository
        self.work = WorkService(self.work_repository)
        self.work_community = CSDNCommunityService()
        self.novel_drafts = NovelDraftService(novel_repository)

    def _create_knowledge_provider(self):
        if settings.knowledge_provider != "ragflow":
            return None
        if not settings.ragflow_api_key:
            raise ValueError("RAGFLOW_API_KEY is required when KNOWLEDGE_PROVIDER=ragflow")
        return RAGFlowKnowledgeProvider(
            client=RAGFlowClient(
                base_url=settings.ragflow_base_url,
                api_key=settings.ragflow_api_key,
                timeout_seconds=settings.ragflow_timeout_seconds,
            ),
                dataset_id=settings.ragflow_dataset_id or None,
                dataset_name=settings.ragflow_dataset_name,
                embedding_model=settings.ragflow_embedding_model,
                llm_model=settings.ragflow_llm_model,
                rerank_model=settings.ragflow_rerank_model,
            )

    def _create_object_storage(self):
        if settings.object_storage_backend == "s3":
            return S3ObjectStorage(
                bucket=settings.object_storage_bucket,
                region=settings.object_storage_region,
                endpoint_url=settings.object_storage_endpoint_url or None,
                access_key_id=settings.object_storage_access_key_id or None,
                secret_access_key=settings.object_storage_secret_access_key or None,
            )
        if settings.object_storage_backend == "local":
            return LocalObjectStorage(settings.object_storage_root)
        return None

    def health(self) -> dict[str, str]:
        return {"status": "ok", "product": settings.app_name}

    def request_registration(self, payload: dict) -> dict[str, object]:
        return self.auth.request_registration(
            email=payload["email"],
            password=payload["password"],
            display_name=payload.get("displayName", ""),
        )

    def _create_english_dictionary_provider(self, backend: str):
        static = StaticEnglishDictionaryProvider()
        # Unit tests use the offline reference. Runtime services retain a
        # replaceable remote provider for vocabulary outside the bundled set.
        if backend == "memory":
            return static
        return FallbackEnglishDictionaryProvider(
            static=static,
            remote=FreeDictionaryProvider(),
        )

    def verify_registration(self, payload: dict) -> dict[str, object]:
        session = self.auth.verify_registration(email=payload["email"], code=payload["code"])
        return {"token": session.token, "user": session.user.to_dict()}

    def login(self, payload: dict) -> dict[str, object]:
        session = self.auth.login(email=payload["email"], password=payload["password"])
        return {"token": session.token, "user": session.user.to_dict()}

    def current_auth_user(self) -> dict[str, str]:
        return self.users.current_user().to_dict()

    def authenticate(self, token: str | None):
        return self.auth.authenticate(token)

    def list_planets(self) -> dict[str, object]:
        return self.universe.portal()

    def get_planet(self, planet_name: str) -> dict[str, object]:
        return self.universe.planet(planet_name)

    def get_work_home(self) -> dict[str, object]:
        user = self.users.current_user()
        self.registry.get_enterable_planet("work")
        return self.work.home(
            user.id,
            knowledge_summary={"documents": []},
        )

    def list_work_cases(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        self.registry.get_enterable_planet("work")
        return self.work.list_practice_cases(user.id)

    def create_work_case(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        self.registry.get_enterable_planet("work")
        return self.work.create_practice_case(user.id, payload)

    def get_work_case(self, case_id: str) -> dict[str, object]:
        user = self.users.current_user()
        self.registry.get_enterable_planet("work")
        return self.work.get_practice_case(user.id, case_id)

    def update_work_case(self, case_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        self.registry.get_enterable_planet("work")
        return self.work.update_practice_case(user.id, case_id, payload)

    def list_work_tech_stacks(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.work.list_tech_stacks(user.id)

    def create_work_tech_stack(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.create_tech_stack(user.id, payload)

    def update_work_tech_stack(self, tech_stack_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.update_tech_stack(user.id, tech_stack_id, payload)

    def delete_work_tech_stack(self, tech_stack_id: str) -> dict[str, object]:
        user = self.users.current_user()
        archived = self.work.archive_tech_stack(user.id, tech_stack_id)
        for grant in self.knowledge.list_share_grants(user.id, tech_stack_id=tech_stack_id):
            self.knowledge.revoke_share_grant(user.id, str(grant["id"]))
        return archived

    def get_work_tech_stack(self, tech_stack_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.tech_stack_detail(
            user.id,
            tech_stack_id,
            knowledge_summary={"documents": self.knowledge.list_work_documents(user.id, tech_stack_id=tech_stack_id)},
        )

    def list_work_articles(self, tech_stack_id: str | None = None) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.work.list_articles(user.id, tech_stack_id=tech_stack_id)

    def create_work_article(self, tech_stack_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.create_article(user.id, tech_stack_id, payload)

    def list_work_learning_records(self, tech_stack_id: str | None = None) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.work.list_learning_records(user.id, tech_stack_id=tech_stack_id)

    def create_work_learning_record(self, tech_stack_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.work.create_learning_record(user.id, tech_stack_id, payload)

    def get_work_community_articles(self, topic: str = "java") -> dict[str, object]:
        self.registry.get_enterable_planet("work")
        return self.work_community.hot_articles(topic=topic, limit=30)

    def get_work_community_article_detail(self, url: str) -> dict[str, str]:
        self.registry.get_enterable_planet("work")
        return self.work_community.article_detail(url)

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

    def list_novel_drafts(self) -> list[dict[str, object]]:
        return self.novel_drafts.list_drafts(self.users.current_user().id)

    def create_novel_draft(self, payload: dict) -> dict[str, object]:
        return self.novel_drafts.create_draft(self.users.current_user().id, payload)

    def update_novel_draft(self, draft_id: str, payload: dict) -> dict[str, object]:
        return self.novel_drafts.update_draft(self.users.current_user().id, draft_id, payload)

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
        workspace = self.study_workspace.workspace(
            user=user,
            planet=planet,
            knowledge_summary=self.knowledge.overview(user.id),
            analytics_summary=analytics,
        )
        current_goal = workspace.get("currentGoal")
        if isinstance(current_goal, dict) and current_goal.get("id"):
            progress = current_goal.get("progress")
            if isinstance(progress, dict):
                progress["masteredItems"] = self._goal_mastered_count(user.id, str(current_goal["id"]))
        return workspace

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

    def create_plan_node(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_plans.create_plan_node(user.id, payload)

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
            scope=payload.get("scope", "current_goal"),
        )

    def save_tutor_answer_event(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_tutor.save_answer_event(user=user, payload=payload)

    def get_knowledge_evidence(self, document_id: str) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.knowledge.evidence(user.id, document_id)

    def get_tutor_history(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.study_tutor.history(user=user)

    def list_wordbook_entries(
        self,
        *,
        goal_id: str | None = None,
        language: str | None = None,
        tag: str | None = None,
    ) -> list[dict[str, object]]:
        user = self.users.current_user()
        if goal_id:
            self.study_repository.get_goal(goal_id, user.id)
        return self.study_wordbook.list_entries(user.id, goal_id=goal_id, language=language, tag=tag)

    def get_wordbook_entry(self, entry_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_wordbook.get_entry(user.id, entry_id)

    def create_wordbook_entry(self, payload: dict[str, object]) -> dict[str, object]:
        user = self.users.current_user()
        payload = self._with_wordbook_goal(payload, user.id)
        entry = self.study_wordbook.create_entry(user.id, payload)
        entry["recallSchedule"] = self.study_recall.ensure(
            user.id, RecallSourceType.WORD_ENTRY, str(entry["id"])
        ).to_dict()
        return entry

    def update_wordbook_entry(self, entry_id: str, payload: dict[str, object]) -> dict[str, object]:
        user = self.users.current_user()
        payload = self._with_wordbook_goal(payload, user.id, default_current_goal=False)
        return self.study_wordbook.update_entry(user.id, entry_id, payload)

    def delete_wordbook_entry(self, entry_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_wordbook.delete_entry(user.id, entry_id)

    def import_wordbook_entries(self, payload: dict[str, object]) -> dict[str, object]:
        user = self.users.current_user()
        payload = self._with_wordbook_goal(payload, user.id)
        return self.study_wordbook.import_entries(user.id, payload)

    def refresh_wordbook_dictionary(self, entry_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_wordbook.refresh_dictionary_entry(user.id, entry_id)

    def review_wordbook_entry(self, entry_id: str, payload: dict[str, object]) -> dict[str, object]:
        user = self.users.current_user()
        remembered = bool(payload.get("remembered"))
        before = self.study_wordbook.get_entry(user.id, entry_id)
        result = "remembered" if remembered else "forgot"
        existing_schedule = self.study_recall.ensure(
            user.id,
            RecallSourceType.WORD_ENTRY,
            entry_id,
        )
        same_day_repeat = (
            existing_schedule.last_reviewed_at is not None
            and existing_schedule.last_reviewed_at.date() == local_today()
            and existing_schedule.last_result == result
        )
        entry = (
            before
            if same_day_repeat
            else self.study_wordbook.review_entry(user.id, entry_id, remembered=remembered)
        )
        if remembered and not same_day_repeat and not bool(before.get("mastered")):
            self._record_goal_mastery(
                user.id,
                entry.get("goalId"),
                event_type="wordbook_entry_mastered",
                summary=f"背过单词：{entry.get('word') or '未命名单词'}",
                metadata={"entryId": entry["id"]},
            )
        entry["recallSchedule"] = self.study_recall.review(
            user.id,
            RecallSourceType.WORD_ENTRY,
            entry_id,
            result=result,
        ).to_dict()
        return entry

    def create_knowledge_document(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        payload = self._prepare_knowledge_document_payload(user.id, payload)
        document = self.knowledge.create_document(user.id, payload)
        return self.knowledge.document_detail(user.id, document.id)["document"]

    def adopt_ragflow_knowledge_document(self, payload: dict) -> dict[str, object]:
        """Expose a controlled backend-only bridge for existing RAGFlow files."""
        user = self.users.current_user()
        payload = self._prepare_knowledge_document_payload(user.id, payload)
        return self.knowledge.adopt_ragflow_document(user.id, payload)

    def _prepare_knowledge_document_payload(self, user_id: str, payload: dict) -> dict:
        payload = dict(payload)
        goal_ids = payload.get("goalIds") if isinstance(payload.get("goalIds"), list) else []
        if payload.get("goalId"):
            goal_ids = [payload["goalId"], *goal_ids]
        goal_ids = list(dict.fromkeys(str(goal_id) for goal_id in goal_ids if goal_id))
        for goal_id in goal_ids:
            self.study_repository.get_goal(goal_id, user_id)
        if payload.get("goalId"):
            goal = self.study_repository.get_goal(str(payload["goalId"]), user_id)
            payload["scopeName"] = goal.goal_name
        if payload.get("planetType") == "work" and payload.get("techStackId"):
            try:
                tech_stack = self.work_repository.get_tech_stack(payload["techStackId"], user_id)
            except KeyError:
                tech_stack = None
            if tech_stack:
                payload["scopeName"] = tech_stack.name
        return payload

    def get_knowledge_document_goal_links(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        document = self.knowledge.document_detail(user.id, document_id)["document"]
        return {
            "documentId": document_id,
            "primaryGoalId": document.get("goalId"),
            "goalIds": document.get("goalIds", []),
        }

    def get_knowledge_reading_progress(self, document_id: str) -> dict[str, object] | None:
        user = self.users.current_user()
        return self.knowledge.get_reading_progress(user.id, document_id)

    def save_knowledge_reading_progress(self, document_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.save_reading_progress(user.id, document_id, payload)

    def replace_knowledge_document_goal_links(self, document_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        goal_ids = payload.get("goalIds", [])
        if not isinstance(goal_ids, list):
            raise ValueError("goalIds must be a list")
        for goal_id in goal_ids:
            self.study_repository.get_goal(str(goal_id), user.id)
        primary_goal_id = payload.get("primaryGoalId")
        if primary_goal_id:
            self.study_repository.get_goal(str(primary_goal_id), user.id)
        elif goal_ids:
            primary_goal_id = goal_ids[0]
        scope_name = None
        if primary_goal_id:
            scope_name = self.study_repository.get_goal(str(primary_goal_id), user.id).goal_name
        document = self.knowledge.update_document(
            user.id,
            document_id,
            {"goalIds": goal_ids, "goalId": primary_goal_id, "scopeName": scope_name},
        )
        return self.knowledge.document_detail(user.id, document.id)["document"]

    def list_knowledge_share_grants(self, document_id: str | None = None) -> list[dict[str, object]]:
        user = self.users.current_user()
        if document_id:
            self.knowledge.document_detail(user.id, document_id)
        return self.knowledge.list_share_grants(user.id, document_id=document_id)

    def create_knowledge_share_grant(self, document_id: str, payload: dict[str, object]) -> dict[str, object]:
        user = self.users.current_user()
        source_goal_id = str(payload.get("sourceGoalId") or "")
        tech_stack_id = str(payload.get("techStackId") or "")
        if not source_goal_id or not tech_stack_id:
            raise ValueError("sourceGoalId and techStackId are required")
        self.study_repository.get_goal(source_goal_id, user.id)
        tech_stack = self.work_repository.get_tech_stack(tech_stack_id, user.id)
        if tech_stack.status == "archived":
            raise ValueError("Cannot grant Knowledge to an archived Tech Stack")
        return self.knowledge.create_share_grant(
            user.id,
            document_id=document_id,
            source_goal_id=source_goal_id,
            tech_stack_id=tech_stack_id,
        )

    def revoke_knowledge_share_grant(self, grant_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.revoke_share_grant(user.id, grant_id)

    def list_knowledge_annotations(self, document_id: str) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.knowledge.list_annotations(user.id, document_id)

    def create_knowledge_annotation(self, document_id: str, payload: dict[str, object]) -> dict[str, object]:
        user = self.users.current_user()
        payload = dict(payload)
        if payload.get("goalId"):
            self.study_repository.get_goal(str(payload["goalId"]), user.id)
        annotation = self.knowledge.create_annotation(user.id, document_id, payload)
        if annotation.get("annotationType") == "card":
            annotation["recallSchedule"] = self.study_recall.ensure(
                user.id, RecallSourceType.ANNOTATION, str(annotation["id"])
            ).to_dict()
        return annotation

    def update_knowledge_annotation(
        self,
        document_id: str,
        annotation_id: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        user = self.users.current_user()
        payload = dict(payload)
        if payload.get("goalId"):
            self.study_repository.get_goal(str(payload["goalId"]), user.id)
        return self.knowledge.update_annotation(user.id, document_id, annotation_id, payload)

    def mark_knowledge_annotation_mastered(
        self,
        document_id: str,
        annotation_id: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        user = self.users.current_user()
        previous = self.knowledge.get_annotation(user.id, document_id, annotation_id)
        mastered = bool(payload.get("mastered", True))
        annotation = self.knowledge.set_annotation_mastered(
            user.id,
            document_id,
            annotation_id,
            mastered,
        )
        if mastered and not bool(previous.get("mastered")):
            self._record_goal_mastery(
                user.id,
                annotation.get("goalId"),
                event_type="knowledge_annotation_mastered",
                summary="背过知识卡片" if annotation.get("annotationType") == "card" else "背过知识笔记",
                metadata={"annotationId": annotation["id"], "documentId": document_id},
            )
        if annotation.get("annotationType") == "card":
            annotation["recallSchedule"] = self.study_recall.review(
                user.id,
                RecallSourceType.ANNOTATION,
                annotation_id,
                result="remembered" if mastered else "forgot",
            ).to_dict()
        return annotation

    def list_recall_schedules(self, *, goal_id: str | None = None) -> list[dict[str, object]]:
        user = self.users.current_user()
        if goal_id:
            self.study_repository.get_goal(goal_id, user.id)
        return self.study_recall.list(user.id, goal_id=goal_id)

    def get_recall_schedule(self, source_type: str, source_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_recall.for_source(user.id, RecallSourceType(source_type), source_id)

    def adjust_recall_schedule(
        self, source_type: str, source_id: str, payload: dict[str, object]
    ) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_recall.adjust(user.id, RecallSourceType(source_type), source_id, payload).to_dict()

    def delete_knowledge_annotation(self, document_id: str, annotation_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.delete_annotation(user.id, document_id, annotation_id)

    def _with_wordbook_goal(
        self,
        payload: dict[str, object],
        user_id: str,
        *,
        default_current_goal: bool = True,
    ) -> dict[str, object]:
        normalized = dict(payload)
        if "goalId" not in normalized and default_current_goal:
            goal = self.study_repository.get_active_goal(user_id)
            normalized["goalId"] = goal.id if goal else None
        if normalized.get("goalId"):
            self.study_repository.get_goal(str(normalized["goalId"]), user_id)
        return normalized

    def _record_goal_mastery(
        self,
        user_id: str,
        goal_id: object,
        *,
        event_type: str,
        summary: str,
        metadata: dict[str, object],
    ) -> None:
        if not goal_id:
            return
        goal = self.study_repository.get_goal(str(goal_id), user_id)
        self.study_repository.save_learning_event(
            LearningEvent(
                user_id=user_id,
                event_type=event_type,
                summary=summary,
                metadata={**metadata, "goalId": goal.id},
            )
        )

    def _goal_mastered_count(self, user_id: str, goal_id: str) -> int:
        return sum(
            1
            for event in self.study_repository.list_learning_events(user_id)
            if event.event_type in {"knowledge_annotation_mastered", "wordbook_entry_mastered"}
            and event.metadata.get("goalId") == goal_id
        )

    def knowledge_overview(self) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.overview(user.id)

    def list_knowledge_documents(
        self,
        *,
        subject: str | None = None,
        topic: str | None = None,
        goal_id: str | None = None,
        planet_type: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[dict[str, object]]:
        user = self.users.current_user()
        if goal_id:
            self.study_repository.get_goal(goal_id, user.id)
        return self.knowledge.list_documents(
            user.id,
            subject=subject,
            topic=topic,
            goal_id=goal_id,
            planet_type=planet_type,
            tech_stack_id=tech_stack_id,
        )

    def list_study_knowledge_documents(
        self,
        *,
        subject: str | None = None,
        topic: str | None = None,
        goal_id: str | None = None,
        planet_type: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[dict[str, object]]:
        user = self.users.current_user()
        self.english_dictionary.ensure_reference(user.id)
        return self.knowledge.list_documents(
            user.id,
            subject=subject,
            topic=topic,
            goal_id=goal_id,
            planet_type=planet_type or "study",
            tech_stack_id=tech_stack_id,
        )

    def list_work_knowledge_documents(
        self,
        *,
        subject: str | None = None,
        topic: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[dict[str, object]]:
        user = self.users.current_user()
        if tech_stack_id:
            self.work_repository.get_tech_stack(tech_stack_id, user.id)
        documents = self.knowledge.list_work_documents(
            user.id,
            subject=subject,
            topic=topic,
            tech_stack_id=tech_stack_id,
        )
        active_stack_ids = {stack.id for stack in self.work_repository.list_tech_stacks(user.id)}
        return [
            document
            for document in documents
            if document["accessMode"] == "owned"
            or any(grant["techStackId"] in active_stack_ids for grant in document["shareGrants"])
        ]

    def get_work_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        detail = self.knowledge.work_document_detail(user.id, document_id)
        if detail["accessMode"] == "granted":
            active_stack_ids = {stack.id for stack in self.work_repository.list_tech_stacks(user.id)}
            if not any(grant["techStackId"] in active_stack_ids for grant in detail["shareGrants"]):
                raise PermissionError("Document is not available in an active Work Tech Stack")
        return detail

    def process_work_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        detail = self.knowledge.work_document_detail(user.id, document_id)
        if detail["accessMode"] != "owned":
            raise PermissionError("Granted Study Knowledge is read-only in Work")
        return self.knowledge.process_document(user.id, document_id)

    def refresh_work_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        detail = self.knowledge.work_document_detail(user.id, document_id)
        if detail["accessMode"] != "owned":
            return detail
        return self.knowledge.refresh_document(user.id, document_id)

    def work_knowledge_overview(self) -> dict[str, object]:
        user = self.users.current_user()
        documents = self.knowledge.list_work_documents(user.id)
        return {
            "documentCount": len(documents),
            "ownedCount": sum(1 for document in documents if document["accessMode"] == "owned"),
            "grantedCount": sum(1 for document in documents if document["accessMode"] == "granted"),
            "documents": documents,
        }

    def get_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.document_detail(user.id, document_id)

    def refresh_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.refresh_document(user.id, document_id)

    def process_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.process_document(user.id, document_id)

    def retry_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.retry_document(user.id, document_id)

    def delete_knowledge_document(self, document_id: str) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.delete_document(user.id, document_id)

    def knowledge_provider_health(self) -> dict[str, object]:
        if not self.knowledge_provider:
            return {"provider": "local", "status": "ok", "experimental": True}
        return self.knowledge_provider.health_check()

    def verify_knowledge_provider_runtime(self) -> dict[str, object]:
        user = self.users.current_user()
        return self.knowledge.verify_provider_runtime(user.id)

    def update_knowledge_document(self, document_id: str, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        payload = dict(payload)
        if "goalId" in payload or "goalIds" in payload:
            goal_ids = payload.get("goalIds") if isinstance(payload.get("goalIds"), list) else []
            if payload.get("goalId"):
                goal_ids = [payload["goalId"], *goal_ids]
            goal_ids = list(dict.fromkeys(str(goal_id) for goal_id in goal_ids if goal_id))
            for goal_id in goal_ids:
                self.study_repository.get_goal(goal_id, user.id)
            if payload.get("goalId"):
                goal = self.study_repository.get_goal(str(payload["goalId"]), user.id)
                payload["scopeName"] = goal.goal_name
            elif "goalIds" in payload and not goal_ids:
                payload["scopeName"] = None
        if payload.get("planetType") == "work" and "techStackId" in payload:
            if payload["techStackId"]:
                try:
                    tech_stack = self.work_repository.get_tech_stack(payload["techStackId"], user.id)
                except KeyError:
                    tech_stack = None
                if tech_stack:
                    payload["scopeName"] = tech_stack.name
            else:
                payload["scopeName"] = None
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
                goal_id=payload.get("goalId"),
                planet_type=payload.get("planetType"),
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

    def get_study_feedback_recommendations(self) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_analytics.recommendations(user=user)

    def create_wrong_question(self, payload: dict) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_review.create_wrong_question(user.id, payload)

    def list_wrong_questions(self) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.study_review.list_wrong_questions(user.id)

    def get_review_queue(self, *, include_future: bool = False) -> list[dict[str, object]]:
        user = self.users.current_user()
        return self.study_review.queue(user.id, include_future=include_future)

    def complete_review_item(self, review_id: str, payload: dict | None = None) -> dict[str, object]:
        user = self.users.current_user()
        return self.study_review.complete(user.id, review_id, payload)


# Service tests import this module without a runtime database. The ASGI factory
# rejects a missing PostgreSQL configuration before it can serve requests; this
# dependency-light facade keeps unit tests independent of external services.
api = (
    ApiFacade(persistence_backend="memory")
    if settings.persistence_backend == "postgres" and not settings.database_url
    else ApiFacade(
        database_path=settings.database_path if settings.persistence_backend == "sqlite" else None,
        persistence_backend=settings.persistence_backend,
        database_url=settings.database_url,
    )
)
