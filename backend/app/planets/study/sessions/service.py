from backend.app.core.dates import local_now, parse_datetime
from backend.app.models import SessionStatus, StudySession
from backend.app.planets.study.repository import StudyRepository


class SessionService:
    def __init__(self, repository: StudyRepository) -> None:
        self._repository = repository

    def start_session(self, user_id: str, payload: dict) -> StudySession:
        task_id = payload.get("taskId")
        subject = payload.get("subject")
        topic = payload.get("topic")
        if task_id:
            task = self._repository.get_task(task_id, user_id)
            subject = subject or task.subject
            topic = topic or task.topic
        if not subject or not topic:
            raise ValueError("subject and topic are required to start a study session")
        session = StudySession(
            user_id=user_id,
            task_id=task_id,
            subject=subject,
            topic=topic,
            start_time=parse_datetime(payload.get("startTime")),
        )
        return self._repository.save_session(session)

    def finish_session(self, user_id: str, session_id: str, payload: dict | None = None) -> StudySession:
        payload = payload or {}
        session = self._repository.get_session(session_id, user_id)
        if session.status == SessionStatus.FINISHED:
            return session

        end_time = parse_datetime(payload.get("endTime")) if payload.get("endTime") else local_now()
        duration = int((end_time - session.start_time).total_seconds() // 60)
        if duration < 1:
            raise ValueError("duration_minutes must be at least 1")

        session.end_time = end_time
        session.duration_minutes = duration
        session.notes = payload.get("notes", session.notes)
        session.feeling = payload.get("feeling", session.feeling)
        session.status = SessionStatus.FINISHED
        session.updated_at = end_time
        return self._repository.save_session(session)

    def list_records(self, user_id: str) -> list[StudySession]:
        return sorted(
            self._repository.list_finished_sessions(user_id),
            key=lambda session: session.start_time,
            reverse=True,
        )

