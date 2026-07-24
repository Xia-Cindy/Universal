from __future__ import annotations

import json

from backend.app.models import Concept, Document, DocumentChunk
from backend.app.persistence.codec import chunk_from_payload, concept_from_payload, document_from_payload, dumps
from backend.app.persistence.sqlite import SQLitePersistence


class SQLiteKnowledgeRepository:
    def __init__(self, persistence: SQLitePersistence) -> None:
        self._db = persistence

    def save_document(self, document: Document) -> Document:
        payload = document.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO documents(id,user_id,payload,goal_id,planet_type,tech_stack_id,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,
                   goal_id=excluded.goal_id,planet_type=excluded.planet_type,tech_stack_id=excluded.tech_stack_id,
                   updated_at=excluded.updated_at""",
                (
                    document.id, document.user_id, dumps(payload), document.goal_id, document.planet_type,
                    document.tech_stack_id, payload["createdAt"], payload["updatedAt"],
                ),
            )
        return document

    def get_document(self, document_id: str, user_id: str) -> Document:
        row = self._db.connection.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        if not row or row["user_id"] != user_id:
            raise PermissionError("Document does not belong to user")
        return document_from_payload(json.loads(row["payload"]))

    def list_documents(self, user_id: str, *, subject: str | None = None, topic: str | None = None, goal_id: str | None = None, planet_type: str | None = None, tech_stack_id: str | None = None) -> list[Document]:
        rows = self._db.connection.execute(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        documents = [document_from_payload(json.loads(row["payload"])) for row in rows]
        if subject:
            documents = [item for item in documents if item.subject == subject]
        if topic:
            documents = [item for item in documents if item.topic == topic]
        if goal_id:
            documents = [item for item in documents if item.goal_id == goal_id]
        if planet_type:
            documents = [item for item in documents if item.planet_type == planet_type]
        if tech_stack_id:
            documents = [item for item in documents if item.tech_stack_id == tech_stack_id]
        return documents

    def replace_chunks(self, document_id: str, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        with self._db.transaction() as db:
            db.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
            for chunk in chunks:
                payload = chunk.to_dict()
                db.execute(
                    "INSERT INTO document_chunks(id,user_id,document_id,chunk_index,payload,created_at) VALUES(?,?,?,?,?,?)",
                    (chunk.id, chunk.user_id, chunk.document_id, chunk.chunk_index, dumps(payload), payload["createdAt"]),
                )
        return chunks

    def list_chunks(self, document_id: str, user_id: str) -> list[DocumentChunk]:
        rows = self._db.connection.execute(
            "SELECT payload FROM document_chunks WHERE document_id = ? AND user_id = ? ORDER BY chunk_index",
            (document_id, user_id),
        ).fetchall()
        return [chunk_from_payload(json.loads(row["payload"])) for row in rows]

    def save_concept(self, concept: Concept) -> Concept:
        payload = concept.to_dict()
        with self._db.transaction() as db:
            db.execute(
                "INSERT INTO concepts(id,user_id,payload,created_at) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                (concept.id, concept.user_id, dumps(payload), payload["createdAt"]),
            )
        return concept

    def list_concepts(self, user_id: str) -> list[Concept]:
        rows = self._db.connection.execute("SELECT payload FROM concepts WHERE user_id = ?", (user_id,)).fetchall()
        return [concept_from_payload(json.loads(row["payload"])) for row in rows]
