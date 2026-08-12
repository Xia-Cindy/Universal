from __future__ import annotations

from backend.app.models import Concept, Document, DocumentChunk, KnowledgeAnnotation, KnowledgeShareGrant
from backend.app.persistence.codec import annotation_from_payload, chunk_from_payload, concept_from_payload, document_from_payload, dumps, knowledge_share_grant_from_payload, loads
from backend.app.persistence.sqlite import SQLitePersistence


class SQLiteKnowledgeRepository:
    def __init__(self, persistence: SQLitePersistence) -> None:
        self._db = persistence

    def save_document(self, document: Document) -> Document:
        payload = document.to_dict()
        with self._db.transaction() as db:
            if getattr(self._db, "backend", "sqlite") == "postgres":
                db.execute(
                    """INSERT INTO documents
                    (id,user_id,file_name,file_type,subject,topic,storage_path,processing_status,error_message,
                     created_at,updated_at,payload,goal_id,planet_type,tech_stack_id,tags,provider,
                     provider_dataset_id,provider_document_id,provider_status,content,content_encoding)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                    file_name=excluded.file_name,file_type=excluded.file_type,subject=excluded.subject,
                    topic=excluded.topic,storage_path=excluded.storage_path,processing_status=excluded.processing_status,
                    error_message=excluded.error_message,payload=excluded.payload,goal_id=excluded.goal_id,
                    planet_type=excluded.planet_type,tech_stack_id=excluded.tech_stack_id,tags=excluded.tags,
                    provider=excluded.provider,provider_dataset_id=excluded.provider_dataset_id,
                    provider_document_id=excluded.provider_document_id,provider_status=excluded.provider_status,
                    content=excluded.content,content_encoding=excluded.content_encoding,updated_at=excluded.updated_at""",
                    (
                        document.id, document.user_id, document.file_name, document.file_type.value,
                        document.subject, document.topic, document.storage_path, document.processing_status.value,
                        document.error_message, payload["createdAt"], payload["updatedAt"], dumps(payload),
                        document.goal_id, document.planet_type, document.tech_stack_id, dumps(document.tags),
                        document.provider, document.provider_dataset_id, document.provider_document_id,
                        document.provider_status, document.content, document.content_encoding,
                    ),
                )
            else:
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
        return document_from_payload(loads(row["payload"]))

    def list_documents(self, user_id: str, *, subject: str | None = None, topic: str | None = None, goal_id: str | None = None, planet_type: str | None = None, tech_stack_id: str | None = None) -> list[Document]:
        rows = self._db.connection.execute(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        documents = [document_from_payload(loads(row["payload"])) for row in rows]
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
                if getattr(self._db, "backend", "sqlite") == "postgres":
                    db.execute(
                        """INSERT INTO document_chunks(id,user_id,document_id,chunk_index,content,metadata,payload,created_at)
                           VALUES(?,?,?,?,?,?,?,?)""",
                        (
                            chunk.id, chunk.user_id, chunk.document_id, chunk.chunk_index, chunk.content,
                            dumps(chunk.metadata), dumps(payload), payload["createdAt"],
                        ),
                    )
                else:
                    db.execute(
                        "INSERT INTO document_chunks(id,user_id,document_id,chunk_index,payload,created_at) VALUES(?,?,?,?,?,?)",
                        (chunk.id, chunk.user_id, chunk.document_id, chunk.chunk_index, dumps(payload), payload["createdAt"]),
                    )
        return chunks

    def delete_document(self, document_id: str, user_id: str) -> Document:
        document = self.get_document(document_id, user_id)
        with self._db.transaction() as db:
            db.execute("DELETE FROM knowledge_annotations WHERE document_id = ?", (document_id,))
            db.execute("DELETE FROM knowledge_share_grants WHERE document_id = ?", (document_id,))
            db.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
            db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return document

    def save_share_grant(self, grant: KnowledgeShareGrant) -> KnowledgeShareGrant:
        payload = grant.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO knowledge_share_grants
                (id,user_id,document_id,source_goal_id,tech_stack_id,payload,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(user_id,document_id,tech_stack_id) DO UPDATE SET
                source_goal_id=excluded.source_goal_id,payload=excluded.payload,updated_at=excluded.updated_at""",
                (
                    grant.id, grant.user_id, grant.document_id, grant.source_goal_id,
                    grant.tech_stack_id, dumps(payload), payload["createdAt"], payload["updatedAt"],
                ),
            )
        return grant

    def list_share_grants(
        self,
        user_id: str,
        *,
        document_id: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[KnowledgeShareGrant]:
        clauses = ["user_id = ?"]
        parameters: list[str] = [user_id]
        if document_id:
            clauses.append("document_id = ?")
            parameters.append(document_id)
        if tech_stack_id:
            clauses.append("tech_stack_id = ?")
            parameters.append(tech_stack_id)
        rows = self._db.connection.execute(
            "SELECT payload FROM knowledge_share_grants WHERE " + " AND ".join(clauses) + " ORDER BY created_at",
            tuple(parameters),
        ).fetchall()
        return [knowledge_share_grant_from_payload(loads(row["payload"])) for row in rows]

    def delete_share_grant(self, grant_id: str, user_id: str) -> KnowledgeShareGrant:
        row = self._db.connection.execute(
            "SELECT payload FROM knowledge_share_grants WHERE id = ? AND user_id = ?", (grant_id, user_id)
        ).fetchone()
        if not row:
            raise KeyError(grant_id)
        grant = knowledge_share_grant_from_payload(loads(row["payload"]))
        with self._db.transaction() as db:
            db.execute("DELETE FROM knowledge_share_grants WHERE id = ? AND user_id = ?", (grant_id, user_id))
        return grant

    def delete_share_grants_for_document(self, document_id: str, user_id: str) -> list[KnowledgeShareGrant]:
        grants = self.list_share_grants(user_id, document_id=document_id)
        with self._db.transaction() as db:
            db.execute(
                "DELETE FROM knowledge_share_grants WHERE document_id = ? AND user_id = ?",
                (document_id, user_id),
            )
        return grants

    def list_chunks(self, document_id: str, user_id: str) -> list[DocumentChunk]:
        rows = self._db.connection.execute(
            "SELECT payload FROM document_chunks WHERE document_id = ? AND user_id = ? ORDER BY chunk_index",
            (document_id, user_id),
        ).fetchall()
        return [chunk_from_payload(loads(row["payload"])) for row in rows]

    def save_concept(self, concept: Concept) -> Concept:
        payload = concept.to_dict()
        with self._db.transaction() as db:
            if getattr(self._db, "backend", "sqlite") == "postgres":
                db.execute(
                    """INSERT INTO concepts(id,user_id,subject,topic,name,source,payload,created_at)
                       VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                       subject=excluded.subject,topic=excluded.topic,name=excluded.name,
                       source=excluded.source,payload=excluded.payload""",
                    (
                        concept.id, concept.user_id, concept.subject, concept.topic, concept.name,
                        concept.source, dumps(payload), payload["createdAt"],
                    ),
                )
            else:
                db.execute(
                    "INSERT INTO concepts(id,user_id,payload,created_at) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                    (concept.id, concept.user_id, dumps(payload), payload["createdAt"]),
                )
        return concept

    def list_concepts(self, user_id: str) -> list[Concept]:
        rows = self._db.connection.execute("SELECT payload FROM concepts WHERE user_id = ?", (user_id,)).fetchall()
        return [concept_from_payload(loads(row["payload"])) for row in rows]

    def save_annotation(self, annotation: KnowledgeAnnotation) -> KnowledgeAnnotation:
        payload = annotation.to_dict()
        with self._db.transaction() as db:
            if getattr(self._db, "backend", "sqlite") == "postgres":
                db.execute(
                    """INSERT INTO knowledge_annotations
                    (id,user_id,document_id,goal_id,annotation_type,mastered,payload,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                    goal_id=excluded.goal_id,annotation_type=excluded.annotation_type,mastered=excluded.mastered,
                    payload=excluded.payload,updated_at=excluded.updated_at""",
                    (
                        annotation.id, annotation.user_id, annotation.document_id, annotation.goal_id,
                        annotation.annotation_type.value, annotation.mastered, dumps(payload),
                        payload["createdAt"], payload["updatedAt"],
                    ),
                )
            else:
                db.execute(
                    """INSERT INTO knowledge_annotations
                    (id,user_id,document_id,goal_id,annotation_type,mastered,payload,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                    goal_id=excluded.goal_id,annotation_type=excluded.annotation_type,mastered=excluded.mastered,
                    payload=excluded.payload,updated_at=excluded.updated_at""",
                    (
                        annotation.id, annotation.user_id, annotation.document_id, annotation.goal_id,
                        annotation.annotation_type.value, int(annotation.mastered), dumps(payload),
                        payload["createdAt"], payload["updatedAt"],
                    ),
                )
        return annotation

    def get_annotation(self, annotation_id: str, user_id: str) -> KnowledgeAnnotation:
        row = self._db.connection.execute(
            "SELECT payload FROM knowledge_annotations WHERE id = ? AND user_id = ?",
            (annotation_id, user_id),
        ).fetchone()
        if not row:
            raise PermissionError("Annotation does not belong to user")
        return annotation_from_payload(loads(row["payload"]))

    def list_annotations(self, document_id: str, user_id: str) -> list[KnowledgeAnnotation]:
        rows = self._db.connection.execute(
            """SELECT payload FROM knowledge_annotations
               WHERE document_id = ? AND user_id = ? ORDER BY created_at""",
            (document_id, user_id),
        ).fetchall()
        return [annotation_from_payload(loads(row["payload"])) for row in rows]

    def delete_annotation(self, annotation_id: str, user_id: str) -> KnowledgeAnnotation:
        annotation = self.get_annotation(annotation_id, user_id)
        with self._db.transaction() as db:
            db.execute("DELETE FROM knowledge_annotations WHERE id = ? AND user_id = ?", (annotation_id, user_id))
        return annotation
