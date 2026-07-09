from collections import Counter, defaultdict

from backend.app.core.dates import local_now
from backend.app.files import FileService, UnsupportedFileTypeError
from backend.app.models import Concept, Document, DocumentChunk, DocumentStatus, DocumentType
from backend.app.knowledge.repository import KnowledgeRepository


class KnowledgeService:
    def __init__(
        self,
        *,
        repository: KnowledgeRepository | None = None,
        file_service: FileService | None = None,
    ) -> None:
        self._repository = repository or KnowledgeRepository()
        self._file_service = file_service or FileService()

    def create_document(self, user_id: str, payload: dict) -> Document:
        file_type = payload["fileType"]
        self._file_service.validate(file_type)
        document = Document(
            user_id=user_id,
            file_name=payload["fileName"],
            file_type=DocumentType(file_type),
            subject=payload["subject"],
            topic=payload["topic"],
            goal_id=payload.get("goalId"),
            content=payload.get("content", ""),
            storage_path=payload.get("storagePath"),
        )
        return self._repository.save_document(document)

    def update_document(self, user_id: str, document_id: str, payload: dict) -> Document:
        document = self._repository.get_document(document_id, user_id)
        if "subject" in payload:
            document.subject = payload["subject"]
        if "topic" in payload:
            document.topic = payload["topic"]
        if "goalId" in payload:
            document.goal_id = payload["goalId"]
        document.updated_at = local_now()
        return self._repository.save_document(document)

    def process_document(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        try:
            document.processing_status = DocumentStatus.PARSING
            document.error_message = None
            document.updated_at = local_now()
            self._repository.save_document(document)

            text = self._file_service.extract_text(
                file_type=document.file_type.value,
                content=document.content,
            )
            document.processing_status = DocumentStatus.CHUNKING
            document.updated_at = local_now()
            self._repository.save_document(document)

            chunk_texts = self._file_service.chunk_text(text)
            if not chunk_texts:
                raise ValueError("No processable text content found")
            chunks = [
                DocumentChunk(
                    user_id=user_id,
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    metadata={
                        "fileName": document.file_name,
                        "goalId": document.goal_id,
                        "subject": document.subject,
                        "topic": document.topic,
                    },
                )
                for index, content in enumerate(chunk_texts)
            ]
            self._repository.replace_chunks(document.id, chunks)
            self._repository.save_concept(
                Concept(
                    user_id=user_id,
                    subject=document.subject,
                    topic=document.topic,
                    name=document.topic,
                )
            )
            document.processing_status = DocumentStatus.PROCESSED
            document.updated_at = local_now()
            self._repository.save_document(document)
            return self.document_detail(user_id, document.id)
        except (UnsupportedFileTypeError, ValueError) as exc:
            document.processing_status = DocumentStatus.FAILED
            document.error_message = str(exc)
            document.updated_at = local_now()
            self._repository.save_document(document)
            return self.document_detail(user_id, document.id)

    def list_documents(
        self,
        user_id: str,
        *,
        subject: str | None = None,
        topic: str | None = None,
        goal_id: str | None = None,
    ) -> list[dict[str, object]]:
        return [
            document.to_dict()
            for document in self._repository.list_documents(
                user_id,
                subject=subject,
                topic=topic,
                goal_id=goal_id,
            )
        ]

    def document_detail(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        chunks = self._repository.list_chunks(document.id, user_id)
        return {
            "document": document.to_dict(),
            "chunks": [chunk.to_dict() for chunk in chunks],
        }

    def overview(self, user_id: str) -> dict[str, object]:
        documents = self._repository.list_documents(user_id)
        statuses = Counter(document.processing_status.value for document in documents)
        subject_map: dict[str, set[str]] = defaultdict(set)
        for document in documents:
            subject_map[document.subject].add(document.topic)
        return {
            "documents": [document.to_dict() for document in documents],
            "statusCounts": dict(statuses),
            "subjects": [
                {
                    "subject": subject,
                    "topics": sorted(topics),
                }
                for subject, topics in sorted(subject_map.items())
            ],
        }
