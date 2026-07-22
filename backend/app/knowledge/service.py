from collections import Counter, defaultdict

from backend.app.core.dates import local_now
from backend.app.files import FileService, UnsupportedFileTypeError
from backend.app.knowledge.providers import KnowledgeProvider
from backend.app.models import Concept, Document, DocumentChunk, DocumentStatus, DocumentType
from backend.app.knowledge.repository import KnowledgeRepository


class KnowledgeService:
    def __init__(
        self,
        *,
        repository: KnowledgeRepository | None = None,
        file_service: FileService | None = None,
        provider: KnowledgeProvider | None = None,
    ) -> None:
        self._repository = repository or KnowledgeRepository()
        self._file_service = file_service or FileService()
        self._provider = provider

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
            content_encoding=payload.get("contentEncoding", "text"),
            storage_path=payload.get("storagePath"),
            provider=self._provider.name if self._provider else "local",
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
        if self._provider:
            return self._process_with_provider(user_id, document)
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

    def _process_with_provider(self, user_id: str, document: Document) -> dict[str, object]:
        try:
            if not document.content and not document.storage_path:
                raise ValueError("RAGFlow processing requires document content or a stored file payload")
            document.processing_status = DocumentStatus.PARSING
            document.error_message = None
            document.provider = self._provider.name
            document.updated_at = local_now()
            self._repository.save_document(document)

            if document.provider_dataset_id and document.provider_document_id:
                provider_dataset_id = str(document.provider_dataset_id)
                provider_document_id = str(document.provider_document_id)
                document.provider_status = document.provider_status or "uploaded"
            else:
                upload = self._provider.upload_document(user_id=user_id, document=document)
                provider_dataset_id = str(upload["datasetId"])
                provider_document_id = str(upload["documentId"])
                document.provider_dataset_id = provider_dataset_id
                document.provider_document_id = provider_document_id
                document.provider_status = str(upload.get("status") or "uploaded")
            document.processing_status = DocumentStatus.CHUNKING
            document.updated_at = local_now()
            self._repository.save_document(document)

            parse_result = self._provider.parse_document(
                user_id=user_id,
                dataset_id=provider_dataset_id,
                document_id=provider_document_id,
            )
            document.provider_status = str(parse_result.get("status") or "chunking")
            chunks = self._provider.list_document_chunks(
                user_id=user_id,
                dataset_id=provider_dataset_id,
                document_id=provider_document_id,
            )
            if chunks:
                self._repository.replace_chunks(
                    document.id,
                    [
                        DocumentChunk(
                            user_id=user_id,
                            document_id=document.id,
                            chunk_index=index,
                            content=str(chunk.get("content", "")),
                            metadata=self._provider_chunk_metadata(
                                chunk=chunk,
                                document=document,
                                provider_document_id=provider_document_id,
                            ),
                        )
                        for index, chunk in enumerate(chunks)
                        if chunk.get("content")
                    ],
                )
                self._repository.save_concept(
                    Concept(
                        user_id=user_id,
                        subject=document.subject,
                        topic=document.topic,
                        name=document.topic,
                    )
                )
                document.processing_status = DocumentStatus.PROCESSED
            else:
                document.processing_status = DocumentStatus.CHUNKING
            document.updated_at = local_now()
            self._repository.save_document(document)
            return self.document_detail(user_id, document.id)
        except (RuntimeError, ValueError) as exc:
            document.processing_status = DocumentStatus.FAILED
            document.error_message = str(exc)
            document.provider_status = "failed"
            document.updated_at = local_now()
            self._repository.save_document(document)
            return self.document_detail(user_id, document.id)

    def _provider_chunk_metadata(
        self,
        *,
        chunk: dict[str, object],
        document: Document,
        provider_document_id: str,
    ) -> dict[str, object]:
        metadata = chunk.get("metadata", {})
        return {
            **(metadata if isinstance(metadata, dict) else {}),
            "fileName": document.file_name,
            "goalId": document.goal_id,
            "subject": document.subject,
            "topic": document.topic,
            "providerChunkId": chunk.get("chunkId"),
            "providerDocumentId": provider_document_id,
        }

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
