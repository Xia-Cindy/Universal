import unittest
from threading import RLock

from backend.app.persistence.postgres import PostgresPersistence, _PostgresConnectionProxy


class FakeOperationalError(Exception):
    pass


class FakeCursor:
    pass


class FakeConnection:
    def __init__(self, *, closed=False, failure=None):
        self.closed = closed
        self.failure = failure
        self.executed = []
        self.cursor = FakeCursor()

    def execute(self, statement, parameters=()):
        self.executed.append((statement, parameters))
        if self.failure:
            failure = self.failure
            self.failure = None
            self.closed = True
            raise failure
        return self.cursor

    def close(self):
        self.closed = True


class FakePsycopg:
    def __init__(self, connections):
        self.connections = iter(connections)

    def connect(self, *_args, **_kwargs):
        return next(self.connections)


def persistence_with(*connections):
    persistence = PostgresPersistence.__new__(PostgresPersistence)
    persistence.dsn = "postgresql://test"
    persistence._dict_row = object()
    persistence._operational_error = FakeOperationalError
    persistence._lock = RLock()
    persistence._psycopg = FakePsycopg(connections[1:])
    persistence._connection = connections[0]
    persistence.connection = _PostgresConnectionProxy(persistence)
    return persistence


class PostgresReconnectTests(unittest.TestCase):
    def test_closed_connection_reconnects_before_write(self):
        closed = FakeConnection(closed=True)
        live = FakeConnection()
        persistence = persistence_with(closed, live)

        cursor = persistence.connection.execute("INSERT INTO sample(id) VALUES (?)", ("one",))

        self.assertIs(cursor, live.cursor)
        self.assertEqual(live.executed, [("INSERT INTO sample(id) VALUES (%s)", ("one",))])

    def test_interrupted_read_reconnects_and_retries_once(self):
        stale = FakeConnection(failure=FakeOperationalError("connection dropped"))
        live = FakeConnection()
        persistence = persistence_with(stale, live)

        cursor = persistence.connection.execute("SELECT * FROM sample WHERE id = ?", ("one",))

        self.assertIs(cursor, live.cursor)
        self.assertEqual(len(stale.executed), 1)
        self.assertEqual(len(live.executed), 1)

    def test_interrupted_write_reconnects_without_replaying_write(self):
        stale = FakeConnection(failure=FakeOperationalError("connection dropped"))
        live = FakeConnection()
        persistence = persistence_with(stale, live)

        with self.assertRaises(FakeOperationalError):
            persistence.connection.execute("INSERT INTO sample(id) VALUES (?)", ("one",))

        self.assertEqual(len(stale.executed), 1)
        self.assertEqual(live.executed, [])
        self.assertIs(persistence._connection, live)


if __name__ == "__main__":
    unittest.main()
