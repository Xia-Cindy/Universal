from backend.app.models import Concept, Document, DocumentChunk, KnowledgeAnnotation, KnowledgeShareGrant

from backend.app.persistence.knowledge import SQLiteKnowledgeRepository

__all__ = ["KnowledgeRepository", "SQLiteKnowledgeRepository"]


class KnowledgeRepository:
    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self.chunks: dict[str, DocumentChunk] = {}
        self.concepts: dict[str, Concept] = {}
        self.annotations: dict[str, KnowledgeAnnotation] = {}
        self.share_grants: dict[tuple[str, str, str], KnowledgeShareGrant] = {}

    def save_document(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    def get_document(self, document_id: str, user_id: str) -> Document:
        document = self.documents[document_id]
        if document.user_id != user_id:
            raise PermissionError("Document does not belong to user")
        return document

    def list_documents(
        self,
        user_id: str,
        *,
        subject: str | None = None,
        topic: str | None = None,
        goal_id: str | None = None,
        planet_type: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[Document]:
        documents = [document for document in self.documents.values() if document.user_id == user_id]
        if subject:
            documents = [document for document in documents if document.subject == subject]
        if topic:
            documents = [document for document in documents if document.topic == topic]
        if goal_id:
            documents = [document for document in documents if document.goal_id == goal_id]
        if planet_type:
            documents = [document for document in documents if document.planet_type == planet_type]
        if tech_stack_id:
            documents = [document for document in documents if document.tech_stack_id == tech_stack_id]
        return sorted(documents, key=lambda document: document.created_at, reverse=True)

    def replace_chunks(self, document_id: str, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        self.chunks = {
            chunk_id: chunk
            for chunk_id, chunk in self.chunks.items()
            if chunk.document_id != document_id
        }
        for chunk in chunks:
            self.chunks[chunk.id] = chunk
        return chunks

    def delete_document(self, document_id: str, user_id: str) -> Document:
        document = self.get_document(document_id, user_id)
        self.documents.pop(document_id, None)
        self.chunks = {
            chunk_id: chunk for chunk_id, chunk in self.chunks.items() if chunk.document_id != document_id
        }
        self.annotations = {
            annotation_id: annotation
            for annotation_id, annotation in self.annotations.items()
            if annotation.document_id != document_id
        }
        self.share_grants = {
            key: grant
            for key, grant in self.share_grants.items()
            if grant.document_id != document_id
        }
        return document

    def save_share_grant(self, grant: KnowledgeShareGrant) -> KnowledgeShareGrant:
        self.share_grants[(grant.user_id, grant.document_id, grant.tech_stack_id)] = grant
        return grant

    def list_share_grants(
        self,
        user_id: str,
        *,
        document_id: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[KnowledgeShareGrant]:
        grants = [grant for grant in self.share_grants.values() if grant.user_id == user_id]
        if document_id:
            grants = [grant for grant in grants if grant.document_id == document_id]
        if tech_stack_id:
            grants = [grant for grant in grants if grant.tech_stack_id == tech_stack_id]
        return sorted(grants, key=lambda grant: grant.created_at)

    def delete_share_grant(self, grant_id: str, user_id: str) -> KnowledgeShareGrant:
        for key, grant in list(self.share_grants.items()):
            if grant.id == grant_id and grant.user_id == user_id:
                self.share_grants.pop(key)
                return grant
        raise KeyError(grant_id)

    def delete_share_grants_for_document(self, document_id: str, user_id: str) -> list[KnowledgeShareGrant]:
        removed = [
            grant
            for grant in self.share_grants.values()
            if grant.document_id == document_id and grant.user_id == user_id
        ]
        self.share_grants = {
            key: grant
            for key, grant in self.share_grants.items()
            if not (grant.document_id == document_id and grant.user_id == user_id)
        }
        return removed

    def list_chunks(self, document_id: str, user_id: str) -> list[DocumentChunk]:
        return sorted(
            [
                chunk
                for chunk in self.chunks.values()
                if chunk.document_id == document_id and chunk.user_id == user_id
            ],
            key=lambda chunk: chunk.chunk_index,
        )

    def save_concept(self, concept: Concept) -> Concept:
        self.concepts[concept.id] = concept
        return concept

    def list_concepts(self, user_id: str) -> list[Concept]:
        return [concept for concept in self.concepts.values() if concept.user_id == user_id]

    def save_annotation(self, annotation: KnowledgeAnnotation) -> KnowledgeAnnotation:
        self.annotations[annotation.id] = annotation
        return annotation

    def get_annotation(self, annotation_id: str, user_id: str) -> KnowledgeAnnotation:
        annotation = self.annotations[annotation_id]
        if annotation.user_id != user_id:
            raise PermissionError("Annotation does not belong to user")
        return annotation

    def list_annotations(self, document_id: str, user_id: str) -> list[KnowledgeAnnotation]:
        return sorted(
            [
                annotation
                for annotation in self.annotations.values()
                if annotation.document_id == document_id and annotation.user_id == user_id
            ],
            key=lambda annotation: annotation.created_at,
        )

    def delete_annotation(self, annotation_id: str, user_id: str) -> KnowledgeAnnotation:
        annotation = self.get_annotation(annotation_id, user_id)
        self.annotations.pop(annotation_id, None)
        return annotation
