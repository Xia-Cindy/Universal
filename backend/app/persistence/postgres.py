from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Iterator

from backend.app.persistence.knowledge import SQLiteKnowledgeRepository
from backend.app.persistence.memory import SQLiteMemoryRepository
from backend.app.persistence.study import SQLiteStudyRepository
from backend.app.persistence.work import SQLiteWorkRepository
from backend.app.planets.novel.repository import SQLiteNovelRepository


class _PostgresConnectionProxy:
    """Keep the repository SQL contract portable between SQLite and psycopg."""

    def __init__(self, persistence) -> None:
        self._persistence = persistence

    def execute(self, statement: str, parameters=()):
        return self._persistence._execute(statement, parameters)

    def __getattr__(self, name):
        return getattr(self._persistence._connection, name)


class PostgresPersistence:
    """PostgreSQL migration runner and transaction boundary for existing repos."""

    backend = "postgres"

    def __init__(self, dsn: str) -> None:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PostgreSQL persistence requires psycopg[binary]. Install backend dependencies first."
            ) from exc
        self.dsn = dsn
        self._psycopg = psycopg
        self._dict_row = dict_row
        self._operational_error = psycopg.OperationalError
        self._lock = RLock()
        self._connection = self._connect()
        self.connection = _PostgresConnectionProxy(self)
        self.migrate()

    def _connect(self):
        return self._psycopg.connect(self.dsn, row_factory=self._dict_row)

    def _ensure_connection_locked(self) -> None:
        if getattr(self._connection, "closed", False):
            self._reconnect_locked()

    def _reconnect_locked(self) -> None:
        previous = getattr(self, "_connection", None)
        if previous is not None:
            try:
                previous.close()
            except Exception:
                pass
        self._connection = self._connect()

    def _execute(self, statement: str, parameters=()):
        sql = statement.replace("?", "%s")
        with self._lock:
            self._ensure_connection_locked()
            try:
                return self._connection.execute(sql, parameters)
            except self._operational_error:
                self._reconnect_locked()
                if _is_retryable_statement(statement):
                    return self._connection.execute(sql, parameters)
                raise

    def migrate(self) -> None:
        migration_dir = Path(__file__).resolve().parents[3] / "database" / "migrations"
        with self._lock:
            self._ensure_connection_locked()
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY)"
            )
            applied = {
                row["version"]
                for row in self._connection.execute("SELECT version FROM schema_migrations")
            }
            for migration in sorted(migration_dir.glob("*.sql")):
                if migration.name in applied:
                    continue
                for statement in _statements(migration.read_text(encoding="utf-8")):
                    self._connection.execute(statement)
                self._connection.execute(
                    "INSERT INTO schema_migrations(version) VALUES (%s)",
                    (migration.name,),
                )
            self._connection.commit()

    @contextmanager
    def transaction(self) -> Iterator[_PostgresConnectionProxy]:
        with self._lock:
            self._ensure_connection_locked()
            try:
                self._connection.execute("BEGIN")
            except self._operational_error:
                self._reconnect_locked()
                self._connection.execute("BEGIN")
            try:
                yield self.connection
            except Exception:
                if not getattr(self._connection, "closed", False):
                    self._connection.rollback()
                raise
            else:
                self._connection.commit()

    def close(self) -> None:
        with self._lock:
            self._connection.close()


def _statements(script: str) -> list[str]:
    return [part.strip() for part in script.split(";") if part.strip()]


def _is_retryable_statement(statement: str) -> bool:
    command = statement.lstrip().split(None, 1)[0].upper() if statement.strip() else ""
    return command in {"SELECT", "SHOW", "WITH"}


class PostgresStudyRepository(SQLiteStudyRepository):
    pass


class PostgresKnowledgeRepository(SQLiteKnowledgeRepository):
    pass


class PostgresMemoryRepository(SQLiteMemoryRepository):
    pass


class PostgresWorkRepository(SQLiteWorkRepository):
    pass


class PostgresNovelRepository(SQLiteNovelRepository):
    pass


__all__ = [
    "PostgresKnowledgeRepository",
    "PostgresMemoryRepository",
    "PostgresNovelRepository",
    "PostgresPersistence",
    "PostgresStudyRepository",
    "PostgresWorkRepository",
]
