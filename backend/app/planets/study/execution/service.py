from backend.app.core.dates import local_now
from backend.app.memory import MemoryService
from backend.app.models import LearningEvent, MemoryScope, SessionStatus, TaskStatus
from backend.app.planets.study.repository import StudyRepository
from backend.app.planets.study.sessions import SessionService


class StudyExecutionService:
    """Product workflow wrapper for active Study Sessions."""

    def __init__(
        self,
        *,
        repository: StudyRepository,
        sessions: SessionService,
        memory: MemoryService,
    ) -> None:
        self._repository = repository
        self._sessions = sessions
        self._memory = memory

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
        existing = self._repository.get_session(session_id, user_id)
        was_finished = existing.status == SessionStatus.FINISHED
        session = self._sessions.finish_session(user_id, session_id, payload)
        if not was_finished:
            self._complete_task_for_session(user_id, session)
            self._record_learning_activity(user_id, session)
            self._write_session_memory(user_id, session)
        return {
            "state": "finished",
            "session": session.to_dict(),
        }

    def _complete_task_for_session(self, user_id: str, session) -> None:
        if not session.task_id:
            return
        task = self._repository.get_task(session.task_id, user_id)
        if task.status != TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            task.completed_at = session.end_time or local_now()
            task.updated_at = task.completed_at
            self._repository.save_daily_task(task)

    def _record_learning_activity(self, user_id: str, session) -> None:
        self._repository.save_learning_event(
            LearningEvent(
                user_id=user_id,
                event_type="study_session_finished",
                summary=f"Finished {session.duration_minutes} minutes on {session.subject} / {session.topic}.",
                metadata={
                    "sessionId": session.id,
                    "taskId": session.task_id,
                    "subject": session.subject,
                    "topic": session.topic,
                    "durationMinutes": session.duration_minutes,
                    "feeling": session.feeling,
                },
            )
        )

    def _write_session_memory(self, user_id: str, session) -> None:
        self._memory.add(
            user_id=user_id,
            scope=MemoryScope.SESSION,
            planet_type="study",
            session_id=session.id,
            key="study_session_result",
            value={
                "subject": session.subject,
                "topic": session.topic,
                "duration_minutes": session.duration_minutes,
                "feeling": session.feeling,
            },
            memory_type="learning_history",
            importance=1,
            metadata={"source": "study_execution"},
        )
        self._memory.add(
            user_id=user_id,
            scope=MemoryScope.PLANET,
            planet_type="study",
            key="recent_learning_activity",
            value={
                "subject": session.subject,
                "topic": session.topic,
                "duration_minutes": session.duration_minutes,
            },
            memory_type="learning_history",
            importance=1,
            metadata={"source": "study_execution", "sessionId": session.id},
        )
