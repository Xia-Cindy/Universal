from backend.app.core.dates import local_now
from backend.app.memory import MemoryService
from backend.app.models import TaskStatus
from backend.app.planets.study.repository import StudyRepository
from backend.app.planets.study.sessions import SessionService
from backend.app.planets.study.execution.unit_of_work import StudySessionFinishUnitOfWork


class StudyExecutionService:
    """Product workflow wrapper for active Study Sessions."""

    def __init__(
        self,
        *,
        repository: StudyRepository,
        sessions: SessionService,
        memory: MemoryService,
        failure_injector=None,
    ) -> None:
        self._repository = repository
        self._sessions = sessions
        self._memory = memory
        self._finish_uow = StudySessionFinishUnitOfWork(
            study_repository=repository,
            memory_repository=memory._repository,
            failure_injector=failure_injector,
        )

    def start(self, user_id: str, payload: dict) -> dict[str, object]:
        session = self._sessions.start_session(user_id, payload)
        if session.task_id:
            task = self._repository.get_task(session.task_id, user_id)
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = local_now()
                self._repository.save_daily_task(task)
        return {
            "state": "active",
            "session": session.to_dict(),
        }

    def finish(self, user_id: str, session_id: str, payload: dict | None = None) -> dict[str, object]:
        session = self._repository.get_session(session_id, user_id)
        session = self._finish_uow.finish(
            user_id,
            session,
            build_finished_session=lambda current: self._sessions.build_finished_session(current, payload),
        )
        return {
            "state": "finished",
            "session": session.to_dict(),
        }
