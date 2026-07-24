from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Iterator

from backend.app.persistence.knowledge import SQLiteKnowledgeRepository
from backend.app.persistence.memory import SQLiteMemoryRepository
from backend.app.persistence.study import SQLiteStudyRepository
from backend.app.persistence.work import SQLiteWorkRepository


class _PostgresConnectionProxy:
    """Keep the repository SQL contract portable between SQLite and psycopg."""

    def __init__(self, connection) -> None:
        self._connection = connection

    def execute(self, statement: str, parameters=()):
        return self._connection.execute(statement.replace("?", "%s"), parameters)

    def __getattr__(self, name):
        return getattr(self._connection, name)


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
        self._connection = psycopg.connect(dsn, row_factory=dict_row)
        self.connection = _PostgresConnectionProxy(self._connection)
        self._lock = RLock()
        self.migrate()

    def migrate(self) -> None:
        migration_dir = Path(__file__).resolve().parents[3] / "database" / "migrations"
        with self._lock:
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
            self._connection.execute("BEGIN")
            try:
                yield self.connection
            except Exception:
                self._connection.rollback()
                raise
            else:
                self._connection.commit()

    def close(self) -> None:
        with self._lock:
            self._connection.close()


def _statements(script: str) -> list[str]:
    return [part.strip() for part in script.split(";") if part.strip()]


class PostgresStudyRepository(SQLiteStudyRepository):
    pass


class PostgresKnowledgeRepository(SQLiteKnowledgeRepository):
    pass


class PostgresMemoryRepository(SQLiteMemoryRepository):
    pass


class PostgresWorkRepository(SQLiteWorkRepository):
    pass


__all__ = [
    "PostgresKnowledgeRepository",
    "PostgresMemoryRepository",
    "PostgresPersistence",
    "PostgresStudyRepository",
    "PostgresWorkRepository",
]
