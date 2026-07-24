from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Iterator


class SQLitePersistence:
    """Small shared SQLite runtime used by the local API process.

    Repositories own domain mapping; this class owns one connection, migration
    execution, and transaction boundaries shared by all repositories.
    """

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(
            self.path,
            check_same_thread=False,
            isolation_level=None,
        )
        self.connection.row_factory = sqlite3.Row
        self._lock = RLock()
        self.migrate()

    def migrate(self) -> None:
        migration_dir = Path(__file__).resolve().parents[3] / "database" / "migrations" / "sqlite"
        with self._lock:
            self.connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY)"
            )
            applied = {
                row[0]
                for row in self.connection.execute("SELECT version FROM schema_migrations")
            }
            for migration in sorted(migration_dir.glob("*.sql")):
                version = migration.name
                if version in applied:
                    continue
                self.connection.executescript(migration.read_text(encoding="utf-8"))
                self.connection.execute(
                    "INSERT INTO schema_migrations(version) VALUES (?)",
                    (version,),
                )

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                yield self.connection
            except Exception:
                self.connection.rollback()
                raise
            else:
                self.connection.commit()

    def close(self) -> None:
        with self._lock:
            self.connection.close()
