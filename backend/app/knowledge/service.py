from collections import Counter, defaultdict
from base64 import b64decode, b64encode
from copy import copy

from backend.app.core.dates import local_now
from backend.app.core.dates import parse_datetime
from backend.app.files import FileService, UnsupportedFileTypeError
from backend.app.knowledge.providers import KnowledgeProvider
from backend.app.models import (
    Concept,
    Document,
    DocumentChunk,
    DocumentStatus,
    DocumentType,
    KnowledgeAnnotation,
    KnowledgeAnnotationType,
    KnowledgeShareGrant,
    ReadingProgress,
)
from backend.app.knowledge.repository import KnowledgeRepository
from backend.app.services.evidence import evidence_source
from backend.app.storage import ObjectStorage


class KnowledgeService:
    def __init__(
        self,
        *,
        repository: KnowledgeRepository | None = None,
        file_service: FileService | None = None,
        provider: KnowledgeProvider | None = None,
        storage: ObjectStorage | None = None,
    ) -> None:
        self._repository = repository or KnowledgeRepository()
        self._file_service = file_service or FileService()
        self._provider = provider
        self._storage = storage

    def create_document(self, user_id: str, payload: dict) -> Document:
        file_type = payload["fileType"]
        self._file_service.validate(file_type)
        goal_ids = self._normalize_goal_ids(payload.get("goalIds"), primary_goal_id=payload.get("goalId"))
        goal_id = self._primary_goal_id(payload.get("goalId"), goal_ids)
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
            scope_name=payload.get("scopeName"),
            tags=tuple(tags),
            content=payload.get("content", ""),
            content_encoding=payload.get("contentEncoding", "text"),
            storage_path=payload.get("storagePath"),
            provider=self._provider.name if self._provider else "local",
        )
        if self._storage and document.content:
            object_key = f"{document.planet_type}/{user_id}/knowledge/{document.id}/{document.file_name}"
            raw_content = (
                b64decode(document.content)
                if document.content_encoding == "base64"
                else document.content.encode("utf-8")
            )
            document.storage_path = self._storage.put(
                object_key,
                raw_content,
                content_type=_content_type(document.file_type.value),
            )
            document.content = ""
        saved = self._repository.save_document(document)
        if saved.planet_type == "study":
            self._repository.replace_document_goal_links(user_id, saved.id, goal_ids)
        return saved

    def verify_provider_runtime(self, user_id: str) -> dict[str, object]:
        """Run one non-mutating provider probe before accepting a new upload.

        A completed RAGFlow-backed document is deliberately reused as the
        retrieval source.  The probe never calls upload, dataset creation, or
        parsing APIs, and it does not persist a status row of its own.
        """
        checked_at = local_now().isoformat()
        if not self._provider or self._provider.name != "ragflow":
            return {
                "provider": self._provider.name if self._provider else "local",
                "status": "failed",
                "verified": False,
                "checkedAt": checked_at,
                "errorCode": "RAGFLOW_NOT_CONFIGURED",
                "message": "当前未启用 RAGFlow，无法执行 embedding/retrieval 运行时验证。",
            }

        source = next(
            (
                document
                for document in self._repository.list_documents(user_id)
                if document.provider == "ragflow"
                and document.processing_status == DocumentStatus.PROCESSED
                and document.provider_dataset_id
                and document.provider_document_id
            ),
            None,
        )
        if not source:
            return {
                "provider": "ragflow",
                "status": "failed",
                "verified": False,
                "checkedAt": checked_at,
                "errorCode": "RAGFLOW_RUNTIME_NO_PROCESSED_SOURCE",
                "message": "没有可用于只读验证的已完成资料，无法安全确认 RAGFlow 当前可用。",
            }

        try:
            probe = self._provider.runtime_probe(
                user_id=user_id,
                dataset_id=str(source.provider_dataset_id),
                document_id=str(source.provider_document_id),
            )
        except (RuntimeError, ValueError) as exc:
            code, message = _runtime_probe_failure(str(exc))
            return {
                "provider": "ragflow",
                "status": "failed",
                "verified": False,
                "checkedAt": checked_at,
                "errorCode": code,
                "message": message,
            }
        if probe.get("status") != "verified":
            return {
                "provider": "ragflow",
                "status": "failed",
                "verified": False,
                "checkedAt": checked_at,
                "errorCode": "RAGFLOW_RUNTIME_PROBE_FAILED",
                "message": "RAGFlow embedding/retrieval 探针未通过。",
            }
        return {
            "provider": "ragflow",
            "status": "verified",
            "verified": True,
            "checkedAt": checked_at,
            "errorCode": None,
            "message": "RAGFlow embedding 与检索探针已通过。",
        }

    def adopt_ragflow_document(self, user_id: str, payload: dict) -> dict[str, object]:
        """Attach a pre-existing RAGFlow document without uploading or parsing it.

        This is deliberately a metadata-only operation for documents created in
        the RAGFlow administration UI.  The provider status lookup validates the
        supplied dataset/document pair before Universe persists its own source
        record; ``refresh_document`` then caches only chunks RAGFlow has already
        made readable.
        """
        if not self._provider or self._provider.name != "ragflow":
            raise ValueError("RAGFlow provider is not configured")
        dataset_id = str(payload.get("providerDatasetId") or "").strip()
        provider_document_id = str(payload.get("providerDocumentId") or "").strip()
        if not dataset_id or not provider_document_id:
            raise ValueError("providerDatasetId and providerDocumentId are required")

        existing = next(
            (
                document
                for document in self._repository.list_documents(user_id)
                if document.provider == self._provider.name
                and document.provider_dataset_id == dataset_id
                and document.provider_document_id == provider_document_id
            ),
            None,
        )
        if existing:
            return self.refresh_document(user_id, existing.id)

        # Do this before creating a local record. A mistyped external ID must not
        # leave a dangling Universe document, and it must never cause a reparse.
        status = self._provider.get_document_status(
            user_id=user_id,
            dataset_id=dataset_id,
            document_id=provider_document_id,
        )
        document = self.create_document(
            user_id,
            {
                **payload,
                "content": "",
                "storagePath": None,
            },
        )
        document.provider = self._provider.name
        document.provider_dataset_id = dataset_id
        document.provider_document_id = provider_document_id
        document.provider_status = str(status.get("status") or "unknown")
        document.provider_error_code = status.get("errorCode")
        document.processing_status = DocumentStatus.CHUNKING
        document.updated_at = local_now()
        self._repository.save_document(document)
        return self.refresh_document(user_id, document.id)

    def update_document(self, user_id: str, document_id: str, payload: dict) -> Document:
        document = self._repository.get_document(document_id, user_id)
        original_planet_type = document.planet_type
        goal_links_updated = "goalIds" in payload or "goalId" in payload
        if "goalIds" in payload:
            next_goal_ids = self._normalize_goal_ids(
                payload.get("goalIds"), primary_goal_id=payload.get("goalId", document.goal_id)
            )
            next_primary_goal_id = self._primary_goal_id(
                payload.get("goalId", document.goal_id), next_goal_ids
            )
        elif "goalId" in payload:
            # Preserve the legacy single-select PATCH meaning for callers that have
            # not adopted goalIds yet. The multi-select client sends goalIds.
            next_goal_ids = self._normalize_goal_ids(None, primary_goal_id=payload.get("goalId"))
            next_primary_goal_id = self._primary_goal_id(payload.get("goalId"), next_goal_ids)
        else:
            next_goal_ids = self._document_goal_ids(user_id, document.id)
            next_primary_goal_id = document.goal_id
        if "fileName" in payload:
            file_name = str(payload["fileName"]).strip()
            if not file_name:
                raise ValueError("fileName is required")
            document.file_name = file_name
        if "subject" in payload:
            document.subject = payload["subject"]
        if "topic" in payload:
            document.topic = payload["topic"]
        if goal_links_updated:
            document.goal_id = next_primary_goal_id
            if "scopeName" in payload:
                document.scope_name = payload.get("scopeName")
            document.tags = tuple(self._normalize_tags(document.tags, goal_id=document.goal_id))
        if "planetType" in payload:
            document.planet_type = payload["planetType"]
            if document.planet_type == "work" and "techStackId" not in payload:
                document.scope_name = None
        if "techStackId" in payload:
            document.tech_stack_id = payload["techStackId"]
            if "scopeName" in payload:
                document.scope_name = payload["scopeName"]
        if "tags" in payload:
            document.tags = tuple(self._normalize_tags(payload["tags"], goal_id=document.goal_id))
        document.updated_at = local_now()
        saved = self._repository.save_document(document)
        if document.planet_type == "study":
            self._repository.replace_document_goal_links(user_id, document.id, next_goal_ids)
        if original_planet_type == "study" and document.planet_type != "study":
            self._repository.delete_share_grants_for_document(document.id, user_id)
        elif document.planet_type == "study":
            self._revoke_invalid_share_grants(user_id, document.id)
        return saved

    def process_document(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        if self._provider:
            return self._process_with_provider(user_id, document)
        try:
            document.processing_status = DocumentStatus.PARSING
            document.error_message = None
            document.provider_error_code = None
            document.updated_at = local_now()
            self._repository.save_document(document)

            content = document.content
            if not content and document.storage_path and self._storage:
                content = self._storage.get(document.storage_path).decode("utf-8")
            text = self._file_service.extract_text(
                file_type=document.file_type.value,
                content=content,
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
                        "goalIds": self._document_goal_ids(user_id, document.id),
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
        """Refresh provider status and cache every readable chunk RAGFlow has produced."""
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
            document.provider_error_code = status.get("errorCode")
            normalized_status = document.provider_status.lower()
            if normalized_status in {"done", "success", "processed", "complete", "completed", "3"}:
                chunks = self._provider.list_document_chunks(
                    user_id=user_id,
                    dataset_id=document.provider_dataset_id,
                    document_id=document.provider_document_id,
                    limit=1000,
                )
                self._cache_provider_chunks(user_id, document, chunks)
                document.processing_status = DocumentStatus.PROCESSED if chunks else DocumentStatus.CHUNKING
                document.error_message = None
                document.provider_error_code = None
            elif normalized_status in {"fail", "failed", "error", "4"}:
                document.processing_status = DocumentStatus.FAILED
                document.error_message = _provider_error_message(
                    status.get("errorMessage")
                    or status.get("progressMessage")
                    or "RAGFlow document processing failed"
                )
            else:
                # RAGFlow emits chunks incrementally for long documents. Cache the
                # readable portion for the bookshelf while keeping the document out
                # of retrieval until parsing reaches a terminal success state.
                chunks = self._provider.list_document_chunks(
                    user_id=user_id,
                    dataset_id=document.provider_dataset_id,
                    document_id=document.provider_document_id,
                    limit=1000,
                )
                self._cache_provider_chunks(user_id, document, chunks)
                document.processing_status = DocumentStatus.CHUNKING
                document.error_message = None
                document.provider_error_code = None
            document.updated_at = local_now()
            self._repository.save_document(document)
            return self.document_detail(user_id, document.id)
        except (RuntimeError, ValueError) as exc:
            if document.processing_status in {DocumentStatus.PARSING, DocumentStatus.CHUNKING}:
                # A status refresh must not turn an in-flight document into a
                # terminal failure when the provider temporarily rejects a
                # preview request (for example, its chunk page-size limit).
                document.error_message = str(exc)
                document.updated_at = local_now()
                self._repository.save_document(document)
                return self.document_detail(user_id, document.id)
            document.processing_status = DocumentStatus.FAILED
            document.provider_status = "failed"
            document.provider_error_code = _provider_error_code(str(exc))
            document.error_message = str(exc)
            document.updated_at = local_now()
            self._repository.save_document(document)
            return self.document_detail(user_id, document.id)

    def retry_document(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        document.processing_status = DocumentStatus.UPLOADED
        document.error_message = None
        document.provider_error_code = None
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
        if self._storage and document.storage_path:
            self._storage.delete(document.storage_path)
        self._repository.delete_document(document.id, user_id)
        return {"id": document.id, "status": "deleted"}

    def _process_with_provider(self, user_id: str, document: Document) -> dict[str, object]:
        try:
            if not document.content and not document.storage_path:
                raise ValueError("RAGFlow processing requires document content or a stored file payload")
            document.processing_status = DocumentStatus.PARSING
            document.error_message = None
            document.provider_error_code = None
            document.provider = self._provider.name
            document.updated_at = local_now()
            self._repository.save_document(document)

            if document.provider_dataset_id and document.provider_document_id:
                provider_dataset_id = str(document.provider_dataset_id)
                provider_document_id = str(document.provider_document_id)
                document.provider_status = document.provider_status or "uploaded"
            else:
                provider_document = document
                if not document.content and document.storage_path and self._storage:
                    provider_document = copy(document)
                    raw_content = self._storage.get(document.storage_path)
                    if document.content_encoding == "base64":
                        provider_document.content = b64encode(raw_content).decode("ascii")
                    else:
                        provider_document.content = raw_content.decode("utf-8")
                upload = self._provider.upload_document(user_id=user_id, document=provider_document)
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
            "goalIds": self._document_goal_ids(document.user_id, document.id),
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
            self._document_payload(user_id, document)
            for document in self._repository.list_documents(
                user_id,
                subject=subject,
                topic=topic,
                goal_id=goal_id,
                planet_type=planet_type,
                tech_stack_id=tech_stack_id,
            )
        ]

    def list_share_grants(
        self,
        user_id: str,
        *,
        document_id: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[dict[str, object]]:
        return [
            grant.to_dict()
            for grant in self._repository.list_share_grants(
                user_id,
                document_id=document_id,
                tech_stack_id=tech_stack_id,
            )
        ]

    def create_share_grant(
        self,
        user_id: str,
        *,
        document_id: str,
        source_goal_id: str,
        tech_stack_id: str,
    ) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        if document.planet_type != "study" or not self._repository.document_has_goal(
            user_id, document.id, source_goal_id
        ):
            raise ValueError("Only a Study document linked to its source Goal can be shared with Work")
        existing = self._repository.list_share_grants(
            user_id,
            document_id=document_id,
            tech_stack_id=tech_stack_id,
        )
        if existing:
            return existing[0].to_dict()
        return self._repository.save_share_grant(
            KnowledgeShareGrant(
                user_id=user_id,
                document_id=document_id,
                source_goal_id=source_goal_id,
                tech_stack_id=tech_stack_id,
            )
        ).to_dict()

    def revoke_share_grant(self, user_id: str, grant_id: str) -> dict[str, object]:
        return self._repository.delete_share_grant(grant_id, user_id).to_dict()

    def list_work_documents(
        self,
        user_id: str,
        *,
        subject: str | None = None,
        topic: str | None = None,
        tech_stack_id: str | None = None,
    ) -> list[dict[str, object]]:
        owned = self._repository.list_documents(
            user_id,
            subject=subject,
            topic=topic,
            planet_type="work",
            tech_stack_id=tech_stack_id,
        )
        grants = self._repository.list_share_grants(user_id, tech_stack_id=tech_stack_id)
        grant_by_document: dict[str, list[KnowledgeShareGrant]] = {}
        for grant in grants:
            grant_by_document.setdefault(grant.document_id, []).append(grant)
        shared = []
        for document_id, document_grants in grant_by_document.items():
            document = self._repository.get_document(document_id, user_id)
            if (
                document.planet_type != "study"
                or any(
                    not self._repository.document_has_goal(user_id, document.id, grant.source_goal_id)
                    for grant in document_grants
                )
            ):
                continue
            if subject and document.subject != subject:
                continue
            if topic and document.topic != topic:
                continue
            shared.append((document, document_grants))
        result = [
            {**self._document_payload(user_id, document), "accessMode": "owned", "shareGrants": []}
            for document in owned
        ]
        result.extend(
            {
                **self._document_payload(user_id, document),
                "accessMode": "granted",
                "shareGrants": [grant.to_dict() for grant in document_grants],
            }
            for document, document_grants in shared
        )
        return sorted(result, key=lambda document: str(document["createdAt"]), reverse=True)

    def work_document_detail(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        if document.planet_type == "work":
            access = {"accessMode": "owned", "shareGrants": []}
        else:
            grants = self._repository.list_share_grants(user_id, document_id=document_id)
            if (
                document.planet_type != "study"
                or not grants
                or any(
                    not self._repository.document_has_goal(user_id, document.id, grant.source_goal_id)
                    for grant in grants
                )
            ):
                raise PermissionError("Document is not available in Work Knowledge")
            access = {"accessMode": "granted", "shareGrants": [grant.to_dict() for grant in grants]}
        return {**self.document_detail(user_id, document_id), **access}

    def document_detail(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        chunks = self._repository.list_chunks(document.id, user_id)
        return {
            "document": self._document_payload(user_id, document),
            "chunks": [chunk.to_dict() for chunk in chunks],
            "annotations": [
                annotation.to_dict()
                for annotation in self._repository.list_annotations(document.id, user_id)
            ],
        }

    def get_reading_progress(self, user_id: str, document_id: str) -> dict[str, object] | None:
        self._repository.get_document(document_id, user_id)
        progress = self._repository.get_reading_progress(user_id, document_id)
        return progress.to_dict() if progress else None

    def save_reading_progress(
        self, user_id: str, document_id: str, payload: dict[str, object]
    ) -> dict[str, object]:
        self._repository.get_document(document_id, user_id)
        spread_index = _required_non_negative_integer(payload.get("spreadIndex"), "spreadIndex")
        page_number = _required_positive_integer(payload.get("pageNumber"), "pageNumber")
        bookmark_label = _nullable_short_text(payload.get("bookmarkLabel"), field_name="bookmarkLabel")
        client_updated_at = parse_datetime(payload.get("clientUpdatedAt"))
        existing = self._repository.get_reading_progress(user_id, document_id)
        if existing and client_updated_at <= existing.client_updated_at:
            return {**existing.to_dict(), "conflictResolution": "server_newer"}
        progress = existing or ReadingProgress(user_id=user_id, document_id=document_id)
        progress.spread_index = spread_index
        progress.page_number = page_number
        progress.bookmark_label = bookmark_label
        progress.client_updated_at = client_updated_at
        progress.updated_at = local_now()
        saved = self._repository.save_reading_progress(progress)
        resolution = "accepted" if saved.id == progress.id else "server_newer"
        return {**saved.to_dict(), "conflictResolution": resolution}

    def list_annotations(self, user_id: str, document_id: str) -> list[dict[str, object]]:
        self._repository.get_document(document_id, user_id)
        return [
            annotation.to_dict()
            for annotation in self._repository.list_annotations(document_id, user_id)
        ]

    def get_annotation(self, user_id: str, document_id: str, annotation_id: str) -> dict[str, object]:
        annotation = self._repository.get_annotation(annotation_id, user_id)
        if annotation.document_id != document_id:
            raise KeyError(annotation_id)
        return annotation.to_dict()

    def create_annotation(
        self,
        user_id: str,
        document_id: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        document = self._repository.get_document(document_id, user_id)
        selected_text = _annotation_text(payload.get("selectedText"))
        if not selected_text:
            raise ValueError("selectedText is required")
        try:
            annotation_type = KnowledgeAnnotationType(str(payload.get("annotationType", "note")))
        except ValueError as exc:
            raise ValueError("annotationType must be note or card") from exc
        annotation = KnowledgeAnnotation(
            user_id=user_id,
            document_id=document.id,
            selected_text=selected_text,
            annotation_type=annotation_type,
            goal_id=_nullable_annotation_text(payload.get("goalId")) or document.goal_id,
            chunk_id=_nullable_annotation_text(payload.get("chunkId")),
            note=_annotation_text(payload.get("note")),
            prompt=_annotation_text(payload.get("prompt")) or selected_text,
            answer=_annotation_text(payload.get("answer")),
            hidden_terms=tuple(_annotation_terms(payload.get("hiddenTerms"))),
        )
        return self._repository.save_annotation(annotation).to_dict()

    def update_annotation(
        self,
        user_id: str,
        document_id: str,
        annotation_id: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        annotation = self._repository.get_annotation(annotation_id, user_id)
        if annotation.document_id != document_id:
            raise KeyError(annotation_id)
        if "goalId" in payload:
            annotation.goal_id = _nullable_annotation_text(payload.get("goalId"))
        for field in ("note", "prompt", "answer"):
            if field in payload:
                setattr(annotation, field, _annotation_text(payload[field]))
        if "hiddenTerms" in payload:
            annotation.hidden_terms = tuple(_annotation_terms(payload["hiddenTerms"]))
        annotation.updated_at = local_now()
        return self._repository.save_annotation(annotation).to_dict()

    def set_annotation_mastered(
        self,
        user_id: str,
        document_id: str,
        annotation_id: str,
        mastered: bool,
    ) -> dict[str, object]:
        annotation = self._repository.get_annotation(annotation_id, user_id)
        if annotation.document_id != document_id:
            raise KeyError(annotation_id)
        annotation.mastered = mastered
        annotation.mastered_at = local_now() if mastered else None
        annotation.updated_at = local_now()
        return self._repository.save_annotation(annotation).to_dict()

    def delete_annotation(self, user_id: str, document_id: str, annotation_id: str) -> dict[str, object]:
        annotation = self._repository.get_annotation(annotation_id, user_id)
        if annotation.document_id != document_id:
            raise KeyError(annotation_id)
        self._repository.delete_annotation(annotation_id, user_id)
        return {"id": annotation_id, "deleted": True}

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
            "documents": [self._document_payload(user_id, document) for document in documents],
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

    def _document_goal_ids(self, user_id: str, document_id: str) -> list[str]:
        return [
            link.goal_id
            for link in self._repository.list_document_goal_links(user_id, document_id=document_id)
        ]

    def _document_payload(self, user_id: str, document: Document) -> dict[str, object]:
        return {**document.to_dict(), "goalIds": self._document_goal_ids(user_id, document.id)}

    @staticmethod
    def _normalize_goal_ids(goal_ids: object, *, primary_goal_id: object = None) -> list[str]:
        values = goal_ids if isinstance(goal_ids, (list, tuple, set)) else []
        normalized = [str(goal_id).strip() for goal_id in values if str(goal_id).strip()]
        if primary_goal_id:
            normalized.insert(0, str(primary_goal_id).strip())
        return list(dict.fromkeys(normalized))

    @staticmethod
    def _primary_goal_id(preferred_goal_id: object, goal_ids: list[str]) -> str | None:
        preferred = str(preferred_goal_id).strip() if preferred_goal_id else None
        if preferred and preferred in goal_ids:
            return preferred
        return goal_ids[0] if goal_ids else None

    def _revoke_invalid_share_grants(self, user_id: str, document_id: str) -> None:
        for grant in self._repository.list_share_grants(user_id, document_id=document_id):
            if not self._repository.document_has_goal(user_id, document_id, grant.source_goal_id):
                self._repository.delete_share_grant(grant.id, user_id)


def _content_type(file_type: str) -> str:
    return {
        "txt": "text/plain",
        "markdown": "text/markdown",
        "pdf": "application/pdf",
    }.get(file_type, "application/octet-stream")


def _annotation_text(value: object) -> str:
    return str(value or "").strip()


def _nullable_annotation_text(value: object) -> str | None:
    value = _annotation_text(value)
    return value or None


def _required_non_negative_integer(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a non-negative integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a non-negative integer") from exc
    if parsed < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return parsed


def _required_positive_integer(value: object, field_name: str) -> int:
    parsed = _required_non_negative_integer(value, field_name)
    if parsed < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return parsed


def _nullable_short_text(value: object, *, field_name: str) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if len(normalized) > 120:
        raise ValueError(f"{field_name} must be 120 characters or fewer")
    return normalized or None


def _annotation_terms(value: object) -> list[str]:
    if isinstance(value, str):
        value = value.split(",")
    if not isinstance(value, (list, tuple)):
        return []
    return list(dict.fromkeys(term for term in (_annotation_text(item) for item in value) if term))


def _provider_error_message(value: object) -> str:
    message = str(value)
    if "InvalidApiKey" in message or "Invalid API-key" in message:
        return (
            "RAGFlow embedding provider rejected its API key (InvalidApiKey). "
            "Check the selected embedding model provider credentials in RAGFlow."
        )
    if "bind embedding model" in message.lower():
        return f"RAGFlow could not bind the embedding model: {message}"
    return message


def _provider_error_code(message: str) -> str | None:
    if "InvalidApiKey" in message or "Invalid API-key" in message:
        return "RAGFLOW_EMBEDDING_INVALID_API_KEY"
    if "bind embedding model" in message.lower():
        return "RAGFLOW_EMBEDDING_MODEL_BIND_FAILED"
    return None


def _runtime_probe_failure(message: str) -> tuple[str, str]:
    """Map provider details to stable, non-secret API diagnostics."""
    normalized = message.lower()
    code = _provider_error_code(message)
    if code == "RAGFLOW_EMBEDDING_INVALID_API_KEY":
        return code, "RAGFlow embedding 凭据无效或未配置。"
    if code == "RAGFLOW_EMBEDDING_MODEL_BIND_FAILED":
        return code, "RAGFlow 无法绑定 embedding 模型。"
    if "timeout" in normalized or "timed out" in normalized:
        return "RAGFLOW_RUNTIME_TIMEOUT", "RAGFlow 运行时探针超时。"
    if "connection" in normalized or "name resolution" in normalized or "dns" in normalized:
        return "RAGFLOW_RUNTIME_CONNECTION_FAILED", "RAGFlow 或其 embedding 服务当前不可连接。"
    if "no retrieval result" in normalized:
        return "RAGFLOW_RUNTIME_NO_RETRIEVAL_RESULT", "RAGFlow 未返回可检索结果，无法确认运行时可用。"
    return "RAGFLOW_RUNTIME_PROBE_FAILED", "RAGFlow embedding/retrieval 探针未通过。"
