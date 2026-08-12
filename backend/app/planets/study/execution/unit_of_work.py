from copy import copy
from typing import Callable

from backend.app.core.dates import local_now
from backend.app.models import LearningEvent, MemoryEntry, MemoryScope, TaskStatus


class StudySessionFinishUnitOfWork:
    """Commit session completion facts together across Study and Memory repositories."""

    def __init__(self, *, study_repository, memory_repository, failure_injector: Callable[[str], None] | None = None):
        self._study = study_repository
        self._memory = memory_repository
        self._failure_injector = failure_injector

    def finish(self, user_id: str, session, *, build_finished_session) -> object:
        persistence = getattr(self._study, "_db", None)
        if persistence is not None:
            # Repository reads use the same connection as writes. Hold the
            # persistence lock from the ownership/status read through the
            # conditional update so a second finish cannot observe an
            # intermediate connection state.
            with persistence._lock:
                return self._finish_persistent(user_id, session, build_finished_session)

        current = self._study.get_session(session.id, user_id)
        if current.status.value == "finished":
            return current
        finished = build_finished_session(current)
        task = self._task_for_session(user_id, finished)
        event, session_memory, planet_memory = self._facts(user_id, finished)
        return self._finish_in_memory(
            current=current, finished=finished, task=task, event=event,
            session_memory=session_memory, planet_memory=planet_memory,
        )

    def _finish_persistent(self, user_id: str, session, build_finished_session) -> object:
        current = self._study.get_session(session.id, user_id)
        if current.status.value == "finished":
            return current
        finished = build_finished_session(current)
        task = self._task_for_session(user_id, finished)
        event, session_memory, planet_memory = self._facts(user_id, finished)
        persistence = self._study._db

        won = False
        with persistence.transaction() as db:
            won = self._study.save_session_in_transaction(db, finished, require_in_progress=True)
            if not won:
                return self._study.get_session(finished.id, user_id)
            self._checkpoint("session")
            if task:
                self._study.save_daily_task_in_transaction(db, task)
            self._checkpoint("task")
            self._study.save_learning_event_in_transaction(db, event)
            self._checkpoint("event")
            self._memory.save_in_transaction(db, session_memory)
            self._checkpoint("session_memory")
            self._memory.save_in_transaction(db, planet_memory)
            self._checkpoint("planet_memory")
        return finished

    def _finish_in_memory(self, *, current, finished, task, event, session_memory, planet_memory):
        # All values are copies/new objects. Restoring snapshots gives tests the
        # same all-or-nothing semantics as persistent adapters.
        sessions = dict(self._study.sessions)
        tasks = dict(self._study.daily_tasks)
        events = dict(self._study.learning_events)
        memories = dict(self._memory.entries)
        try:
            self._study.save_session(finished)
            self._checkpoint("session")
            if task:
                self._study.save_daily_task(task)
            self._checkpoint("task")
            self._study.save_learning_event(event)
            self._checkpoint("event")
            self._memory.save(session_memory)
            self._checkpoint("session_memory")
            self._memory.save(planet_memory)
            self._checkpoint("planet_memory")
        except Exception:
            self._study.sessions = sessions
            self._study.daily_tasks = tasks
            self._study.learning_events = events
            self._memory.entries = memories
            raise
        return finished

    def _task_for_session(self, user_id: str, session):
        if not session.task_id:
            return None
        task = self._study.get_task(session.task_id, user_id)
        if task.status == TaskStatus.COMPLETED:
            return None
        completed = copy(task)
        completed.status = TaskStatus.COMPLETED
        completed.completed_at = session.end_time or local_now()
        completed.updated_at = completed.completed_at
        return completed

    @staticmethod
    def _facts(user_id: str, session):
        event = LearningEvent(
            user_id=user_id,
            event_type="study_session_finished",
            summary=f"Finished {session.duration_minutes} minutes on {session.subject} / {session.topic}.",
            metadata={"sessionId": session.id, "taskId": session.task_id, "subject": session.subject,
                      "topic": session.topic, "durationMinutes": session.duration_minutes, "feeling": session.feeling},
            id=f"study-session:{session.id}",
        )
        session_memory = MemoryEntry(
            user_id=user_id, scope=MemoryScope.SESSION, planet_type="study", session_id=session.id,
            key="study_session_result", value={"subject": session.subject, "topic": session.topic,
            "duration_minutes": session.duration_minutes, "feeling": session.feeling},
            memory_type="learning_history", importance=1, metadata={"source": "study_execution"},
            id=f"study-session:{session.id}:session",
        )
        planet_memory = MemoryEntry(
            user_id=user_id, scope=MemoryScope.PLANET, planet_type="study", key="recent_learning_activity",
            value={"subject": session.subject, "topic": session.topic, "duration_minutes": session.duration_minutes},
            memory_type="learning_history", importance=1,
            metadata={"source": "study_execution", "sessionId": session.id},
            id=f"study-session:{session.id}:planet",
        )
        return event, session_memory, planet_memory

    def _checkpoint(self, stage: str) -> None:
        if self._failure_injector:
            self._failure_injector(stage)
