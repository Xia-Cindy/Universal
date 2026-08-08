import unittest

from backend.app.models import MemoryEntry, MemoryScope
from backend.app.persistence.memory import SQLiteMemoryRepository


class _Transaction:
    def __init__(self, statements):
        self.statements = statements

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, statement, parameters=()):
        self.statements.append((statement, parameters))


class _PostgresPersistence:
    backend = "postgres"

    def __init__(self):
        self.statements = []

    def transaction(self):
        return _Transaction(self.statements)


class PostgresMemoryCompatibilityTests(unittest.TestCase):
    def test_memory_write_populates_legacy_key_and_value_columns(self):
        persistence = _PostgresPersistence()
        repository = SQLiteMemoryRepository(persistence)
        entry = MemoryEntry(
            id="memory-1", user_id="user-1", scope=MemoryScope.PLANET,
            planet_type="study", key="recent_learning_activity", value={"subject": "systems"},
        )

        repository.save(entry)

        statement, parameters = persistence.statements[0]
        self.assertIn("key,value", statement)
        self.assertEqual(parameters[5], "recent_learning_activity")
        self.assertEqual(parameters[6], '{"subject":"systems"}')


if __name__ == "__main__":
    unittest.main()
