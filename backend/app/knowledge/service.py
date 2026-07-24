from collections import Counter, defaultdict

from backend.app.core.dates import local_now
from backend.app.files import FileService, UnsupportedFileTypeError
from backend.app.knowledge.providers import KnowledgeProvider
from backend.app.models import Concept, Document, DocumentChunk, DocumentStatus, DocumentType
from backend.app.knowledge.repository import KnowledgeRepository
from backend.app.services.evidence import evidence_source


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
        goal_id = payload.get("goalId")
        tags = self._normalize_tags(payload.get("tags", []), goal_id=goal_id)
        document = Document(
            user_id=user_id,
            file_name=payload["fileName"],
            file_type=DocumentType(file_type),
            subject=payload["subject"],
            topic=payload["topic"],
            goal_id=goal_id,
            planet_type=payload.get("planetType", "study"),
            tech_stack_id=payload.get("techStackId"),
            tags=tuple(tags),
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
            document.tags = tuple(self._normalize_tags(document.tags, goal_id=document.goal_id))
        if "planetType" in payload:
            document.planet_type = payload["planetType"]
        if "techStackId" in payload:
            document.tech_stack_id = payload["techStackId"]
        if "tags" in payload:
            document.tags = tuple(self._normalize_tags(payload["tags"], goal_id=document.goal_id))
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
                        "planetType": document.planet_type,
                        "techStackId": document.tech_stack_id,
                        "tags": list(document.tags),
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

    def refresh_document(self, user_id: str, document_id: str) -> dict[str, object]:
        """Refresh provider status and cache chunks once processing completes."""
        document = self._repository.get_document(document_id, user_id)
        if not self._provider or not document.provider_dataset_id or not document.provider_document_id:
            return self.document_detail(user_id, document.id)
        try:
            status = self._provider.get_document_status(
                user_id=user_id,
                dataset_id=document.provider_dataset_id,
                document_id=document.provider_document_id,
            )
            document.provider_status = str(status.get("status") or "unknown")
            normalized_status = document.provider_status.lower()
            if normalized_status in {"done", "success", "processed", "complete", "completed", "3"}:
                chunks = self._provider.list_document_chunks(
                    user_id=user_id,
                    dataset_id=document.provider_dataset_id,
                    document_id=document.provider_document_id,
                )
                self._cache_provider_chunks(user_id, document, chunks)
                document.processing_status = DocumentStatus.PROCESSED if chunks else DocumentStatus.CHUNKING
                document.error_message = None
            elif normalized_status in {"fail", "failed", "error", "4"}:
                document.processing_status = DocumentStatus.FAILED
                document.error_message = str(status.get("errorMessage") or "RAGFlow document processing failed")
            else:
                document.processing_status = DocumentStatus.CHUNKING
            document.updated_at = local_now()
            self._repository.save_document(document)
            return self.document_detail(user_id, document.id)
        except (RuntimeError, ValueError) as exc:
            document.processing_status = DocumentStatus.FAILED
            document.provider_status = "failed"
            document.error_message = str(exc)
            document.updated_at = local_now()
            self._repository.save_document(document)
            return self.document_detail(user_id, document.id)

    def retry_document(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        document.processing_status = DocumentStatus.UPLOADED
        document.error_message = None
        document.provider_status = None
        document.updated_at = local_now()
        self._repository.save_document(document)
        return self.process_document(user_id, document.id)

    def delete_document(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        if self._provider and document.provider_dataset_id and document.provider_document_id:
            self._provider.delete_document(
                user_id=user_id,
                dataset_id=document.provider_dataset_id,
                document_id=document.provider_document_id,
            )
        self._repository.delete_document(document.id, user_id)
        return {"id": document.id, "status": "deleted"}

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
            document.updated_at = local_now()
            self._repository.save_document(document)
            if hasattr(self._provider, "get_document_status"):
                return self.refresh_document(user_id, document.id)
            chunks = self._provider.list_document_chunks(
                user_id=user_id,
                dataset_id=provider_dataset_id,
                document_id=provider_document_id,
            )
            self._cache_provider_chunks(user_id, document, chunks)
            document.processing_status = DocumentStatus.PROCESSED if chunks else DocumentStatus.CHUNKING
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

    def _cache_provider_chunks(self, user_id: str, document: Document, chunks: list[dict[str, object]]) -> None:
        valid_chunks = [chunk for chunk in chunks if chunk.get("content")]
        if not valid_chunks:
            return
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
                        provider_document_id=str(document.provider_document_id),
                    ),
                )
                for index, chunk in enumerate(valid_chunks)
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
            "planetType": document.planet_type,
            "techStackId": document.tech_stack_id,
            "tags": list(document.tags),
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
        planet_type: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[dict[str, object]]:
        return [
            document.to_dict()
            for document in self._repository.list_documents(
                user_id,
                subject=subject,
                topic=topic,
                goal_id=goal_id,
                planet_type=planet_type,
                tech_stack_id=tech_stack_id,
            )
        ]

    def document_detail(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        chunks = self._repository.list_chunks(document.id, user_id)
        return {
            "document": document.to_dict(),
            "chunks": [chunk.to_dict() for chunk in chunks],
        }

    def evidence(self, user_id: str, document_id: str) -> list[dict[str, object]]:
        document = self._repository.get_document(document_id, user_id)
        return [
            evidence_source(
                {
                    "documentId": document.id,
                    "chunkId": chunk.id,
                    "content": chunk.content,
                    "metadata": {
                        **chunk.metadata,
                        "fileName": document.file_name,
                        "goalId": document.goal_id,
                        "subject": document.subject,
                        "topic": document.topic,
                    },
                    "score": 1.0,
                    "identifiers": {"documentId": document.id, "chunkId": chunk.id},
                }
            )
            for chunk in self._repository.list_chunks(document.id, user_id)
        ]

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

    def _normalize_tags(self, tags: object, *, goal_id: str | None = None) -> list[str]:
        normalized = []
        if isinstance(tags, (list, tuple)):
            normalized = [str(tag).strip() for tag in tags if str(tag).strip()]
        elif isinstance(tags, str):
            normalized = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if goal_id:
            normalized.append(f"goal:{goal_id}")
        return list(dict.fromkeys(normalized))
