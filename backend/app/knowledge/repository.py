from backend.app.models import Concept, Document, DocumentChunk


class KnowledgeRepository:
    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self.chunks: dict[str, DocumentChunk] = {}
        self.concepts: dict[str, Concept] = {}

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
    ) -> list[Document]:
        documents = [document for document in self.documents.values() if document.user_id == user_id]
        if subject:
            documents = [document for document in documents if document.subject == subject]
        if topic:
            documents = [document for document in documents if document.topic == topic]
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

