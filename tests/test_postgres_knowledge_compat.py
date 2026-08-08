import unittest

from backend.app.models import Concept, Document, DocumentChunk, DocumentType
from backend.app.persistence.knowledge import SQLiteKnowledgeRepository


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


class PostgresKnowledgeCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.persistence = _PostgresPersistence()
        self.repository = SQLiteKnowledgeRepository(self.persistence)

    def test_document_write_populates_normalized_columns(self):
        document = Document(
            id="document-1", user_id="user-1", file_name="notes.md", file_type=DocumentType.MARKDOWN,
            subject="systems", topic="memory", content="# Notes", goal_id="goal-1",
        )

        self.repository.save_document(document)

        statement, parameters = self.persistence.statements[0]
        self.assertIn("file_name,file_type,subject,topic", statement)
        self.assertEqual(parameters[2:6], ("notes.md", "markdown", "systems", "memory"))

    def test_chunk_and_concept_writes_populate_normalized_columns(self):
        chunk = DocumentChunk(
            id="chunk-1", user_id="user-1", document_id="document-1", chunk_index=0,
            content="Knowledge text", metadata={"topic": "memory"},
        )
        concept = Concept(
            id="concept-1", user_id="user-1", subject="systems", topic="memory", name="Memory",
        )

        self.repository.replace_chunks("document-1", [chunk])
        self.repository.save_concept(concept)

        statements = [statement for statement, _ in self.persistence.statements]
        self.assertIn("INSERT INTO document_chunks", statements[1])
        self.assertIn("content,metadata,payload", statements[1])
        self.assertIn("INSERT INTO concepts", statements[2])
        self.assertIn("subject,topic,name,source,payload", statements[2])


if __name__ == "__main__":
    unittest.main()
