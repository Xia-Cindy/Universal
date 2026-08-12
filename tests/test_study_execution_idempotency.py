import unittest
from datetime import timedelta
import os
import tempfile
from pathlib import Path
from threading import Barrier, Thread

from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_now, local_today


class StudyExecutionIdempotencyTests(unittest.TestCase):
    def _started_session(self, api):
        api.create_onboarding_goal({
            "goalName": "Execution retry", "goalType": "learning", "subjects": ["systems"],
            "currentLevel": "beginner", "dailyAvailableMinutes": 30,
        })
        task = api.create_plan({"startDate": local_today().isoformat()})["dailyTasks"][0]
        start_time = local_now().replace(second=0, microsecond=0)
        session = api.start_execution_session({"taskId": task["id"], "startTime": start_time.isoformat()})["session"]
        return task, session, start_time

    def test_session_finish_retry_keeps_one_event_and_two_memory_records(self):
        api = ApiFacade()
        task, session, start_time = self._started_session(api)

        api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=15)).isoformat()})
        api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=45)).isoformat()})

        events = api.study_repository.list_learning_events("local-user")
        memory = api.list_memory(planet_type="study", include_inactive=False)
        session_memory = [item for item in memory if item.get("sessionId") == session["id"]]
        planet_memory = [
            item for item in memory
            if item["metadata"].get("sessionId") == session["id"] and item["key"] == "recent_learning_activity"
        ]

        self.assertEqual(len(events), 1)
        self.assertEqual(len(session_memory), 1)
        self.assertEqual(len(planet_memory), 1)

    def test_memory_repository_rollback_at_every_finish_write_point(self):
        for stage in ("session", "task", "event", "session_memory", "planet_memory"):
            api = ApiFacade()
            task, session, start_time = self._started_session(api)
            api.study_execution._finish_uow._failure_injector = (
                lambda checkpoint, expected=stage: (_ for _ in ()).throw(RuntimeError(expected))
                if checkpoint == expected else None
            )

            with self.assertRaises(RuntimeError):
                api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=15)).isoformat()})

            self.assertEqual(api.study_repository.get_session(session["id"], "local-user").status.value, "in_progress")
            self.assertNotEqual(api.study_repository.get_task(task["id"], "local-user").status.value, "completed")
            self.assertEqual(api.study_repository.list_learning_events("local-user"), [])
            self.assertEqual(
                [item for item in api.list_memory(planet_type="study", include_inactive=False) if item.get("sessionId") == session["id"]],
                [],
            )

    def test_sqlite_rollback_is_atomic_and_retry_commits_all_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            api = ApiFacade(database_path=str(Path(directory) / "execution.sqlite3"))
            task, session, start_time = self._started_session(api)
            api.study_execution._finish_uow._failure_injector = (
                lambda stage: (_ for _ in ()).throw(RuntimeError("memory failure"))
                if stage == "session_memory" else None
            )
            with self.assertRaises(RuntimeError):
                api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=15)).isoformat()})
            self.assertEqual(api.study_repository.get_session(session["id"], "local-user").status.value, "in_progress")
            self.assertNotEqual(api.study_repository.get_task(task["id"], "local-user").status.value, "completed")
            self.assertEqual(api.study_repository.list_learning_events("local-user"), [])
            self.assertEqual(
                [item for item in api.memory.list_for_user("local-user") if item.session_id == session["id"] or item.metadata.get("sessionId") == session["id"]],
                [],
            )

            api.study_execution._finish_uow._failure_injector = None
            api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=15)).isoformat()})
            self.assertEqual(api.study_repository.get_session(session["id"], "local-user").status.value, "finished")
            self.assertEqual(api.study_repository.get_task(task["id"], "local-user").status.value, "completed")
            self.assertEqual(len(api.study_repository.list_learning_events("local-user")), 1)
            self.assertEqual(
                len([item for item in api.memory.list_for_user("local-user") if item.session_id == session["id"] or item.metadata.get("sessionId") == session["id"]]),
                2,
            )
            api.persistence.close()

    def test_sqlite_concurrent_finish_returns_the_same_first_completion(self):
        """The conditional session update is the single winner for concurrent requests."""
        with tempfile.TemporaryDirectory() as directory:
            api = ApiFacade(database_path=str(Path(directory) / "execution.sqlite3"))
            task, session, start_time = self._started_session(api)
            barrier = Barrier(2)
            results = []
            errors = []

            def finish(end_time):
                try:
                    barrier.wait()
                    results.append(api.finish_execution_session(session["id"], {"endTime": end_time.isoformat()}))
                except Exception as exc:  # pragma: no cover - assertions run below
                    errors.append(exc)

            first = Thread(target=finish, args=(start_time + timedelta(minutes=15),))
            second = Thread(target=finish, args=(start_time + timedelta(minutes=45),))
            first.start()
            second.start()
            first.join()
            second.join()

            self.assertEqual(errors, [])
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]["session"], results[1]["session"])
            self.assertEqual(results[0]["session"]["status"], "finished")
            self.assertEqual(api.study_repository.get_task(task["id"], "local-user").status.value, "completed")
            self.assertEqual(len(api.study_repository.list_learning_events("local-user")), 1)
            self.assertEqual(
                len([item for item in api.memory.list_for_user("local-user") if item.session_id == session["id"] or item.metadata.get("sessionId") == session["id"]]),
                2,
            )
            api.persistence.close()


@unittest.skipUnless(os.getenv("UNIVERSE_POSTGRES_TEST_DSN"), "requires isolated PostgreSQL test DSN")
class StudyExecutionPostgresIntegrationTests(unittest.TestCase):
    """Runs the same atomic failure contract against a caller-provided isolated schema."""

    _started_session = StudyExecutionIdempotencyTests._started_session

    def test_postgres_rollback_is_atomic_and_retry_commits_all_facts(self):
        api = ApiFacade(
            persistence_backend="postgres",
            database_url=os.environ["UNIVERSE_POSTGRES_TEST_DSN"],
        )
        task, session, start_time = self._started_session(api)
        api.study_execution._finish_uow._failure_injector = (
            lambda stage: (_ for _ in ()).throw(RuntimeError("postgres memory failure"))
            if stage == "session_memory" else None
        )
        with self.assertRaises(RuntimeError):
            api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=15)).isoformat()})

        self.assertEqual(api.study_repository.get_session(session["id"], "local-user").status.value, "in_progress")
        self.assertNotEqual(api.study_repository.get_task(task["id"], "local-user").status.value, "completed")
        self.assertEqual(api.study_repository.list_learning_events("local-user"), [])

        api.study_execution._finish_uow._failure_injector = None
        api.finish_execution_session(session["id"], {"endTime": (start_time + timedelta(minutes=15)).isoformat()})
        self.assertEqual(api.study_repository.get_session(session["id"], "local-user").status.value, "finished")
        self.assertEqual(api.study_repository.get_task(task["id"], "local-user").status.value, "completed")
        self.assertEqual(len(api.study_repository.list_learning_events("local-user")), 1)
        self.assertEqual(
            len([item for item in api.memory.list_for_user("local-user") if item.session_id == session["id"] or item.metadata.get("sessionId") == session["id"]]),
            2,
        )
        api.persistence.close()

if __name__ == "__main__":
    unittest.main()
