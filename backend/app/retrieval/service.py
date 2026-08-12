from backend.app.core.dates import local_now
from backend.app.knowledge.repository import KnowledgeRepository
from backend.app.knowledge.providers import KnowledgeProvider
from backend.app.models import DocumentStatus
from backend.app.retrieval.embedding import DeterministicEmbeddingProvider, EmbeddingProvider
from backend.app.retrieval.models import ChunkEmbeddingRecord, EmbeddingStatus, RetrievalQuery, RetrievalResult
from backend.app.retrieval.repository import RetrievalRepository
from backend.app.retrieval.vector_store import InMemoryVectorStore, VectorStore


class RetrievalService:
    def __init__(
        self,
        *,
        knowledge_repository: KnowledgeRepository,
        repository: RetrievalRepository | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
        knowledge_provider: KnowledgeProvider | None = None,
    ) -> None:
        self._knowledge_repository = knowledge_repository
        self._repository = repository or RetrievalRepository()
        self._embedding_provider = embedding_provider or DeterministicEmbeddingProvider()
        self._vector_store = vector_store or InMemoryVectorStore()
        self._knowledge_provider = knowledge_provider

    def prepare_document_embeddings(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._knowledge_repository.get_document(document_id, user_id)
        if self._knowledge_provider:
            return {
                "documentId": document.id,
                "status": "provider_backed" if document.provider_document_id else "not_ready",
                "provider": document.provider,
                "providerDatasetId": document.provider_dataset_id,
                "providerDocumentId": document.provider_document_id,
                "records": self.list_document_embeddings(user_id, document.id),
            }
        if document.processing_status != DocumentStatus.PROCESSED:
            return {
                "documentId": document.id,
                "status": "not_ready",
                "records": self.list_document_embeddings(user_id, document.id),
            }

        chunks = self._knowledge_repository.list_chunks(document.id, user_id)
        records = [self._prepare_chunk_embedding(user_id=user_id, chunk=chunk) for chunk in chunks]
        return {
            "documentId": document.id,
            "status": "prepared",
            "records": [record.to_dict() for record in records],
        }

    def list_document_embeddings(self, user_id: str, document_id: str) -> list[dict[str, object]]:
        self._knowledge_repository.get_document(document_id, user_id)
        return [
            record.to_dict()
            for record in self._repository.list_records(user_id=user_id, document_id=document_id)
        ]

    def search(self, query: RetrievalQuery) -> dict[str, object]:
        if self._knowledge_provider:
            return self._provider_search(query)
        embedding = self._embedding_provider.embed(query.query)
        filters = {"userId": query.user_id}
        if query.document_id:
            filters["documentId"] = query.document_id
        if query.goal_id:
            filters["documentIds"] = {
                document.id
                for document in self._knowledge_repository.list_documents(query.user_id, goal_id=query.goal_id)
            }
        if query.planet_type:
            filters["planetType"] = query.planet_type
        matches = self._vector_store.search(
            query_vector=embedding.vector,
            limit=query.limit,
            filters=filters,
        )
        results = [
            RetrievalResult(
                document_id=match.payload["documentId"],
                chunk_id=match.payload["chunkId"],
                content=match.payload["content"],
                metadata=match.payload["metadata"],
                score=match.score,
                identifiers={
                    "embeddingRef": match.vector_ref,
                    "documentId": match.payload["documentId"],
                    "chunkId": match.payload["chunkId"],
                },
            ).to_dict()
            for match in matches
        ]
        return {
            "query": query.query,
            "results": results,
        }

    def _provider_search(self, query: RetrievalQuery) -> dict[str, object]:
        documents = []
        if query.document_id:
            documents = [self._knowledge_repository.get_document(query.document_id, query.user_id)]
        else:
            documents = self._knowledge_repository.list_documents(query.user_id, goal_id=query.goal_id)
        if query.planet_type:
            documents = [document for document in documents if document.planet_type == query.planet_type]
        provider_documents = [
            document
            for document in documents
            if (
                document.processing_status == DocumentStatus.PROCESSED
                and document.provider_dataset_id
                and document.provider_document_id
            )
        ]
        dataset_ids = sorted({str(document.provider_dataset_id) for document in provider_documents})
        document_ids = [str(document.provider_document_id) for document in provider_documents]
        if not dataset_ids:
            return {"query": query.query, "results": []}
        provider_result = self._knowledge_provider.search(
            user_id=query.user_id,
            query=query.query,
            dataset_ids=dataset_ids,
            # A RAGFlow dataset is reusable across uploads. Always constrain the
            # provider request to the Universe documents in the current scope so
            # stale, failed, or otherwise inaccessible provider documents cannot
            # become evidence for this answer.
            document_ids=document_ids,
            limit=query.limit,
        )
        return self._normalize_provider_search_result(
            query=query,
            provider_result=provider_result,
            documents=provider_documents,
        )

    def _normalize_provider_search_result(
        self,
        *,
        query: RetrievalQuery,
        provider_result: dict[str, object],
        documents,
    ) -> dict[str, object]:
        document_by_provider_id = {
            str(document.provider_document_id): document for document in documents if document.provider_document_id
        }
        chunk_by_provider_id = {}
        for document in documents:
            for chunk in self._knowledge_repository.list_chunks(document.id, query.user_id):
                provider_chunk_id = chunk.metadata.get("providerChunkId")
                if provider_chunk_id:
                    chunk_by_provider_id[str(provider_chunk_id)] = chunk

        normalized_results = []
        for result in provider_result.get("results", []):
            if not isinstance(result, dict):
                continue
            normalized = dict(result)
            metadata = normalized.get("metadata", {})
            metadata = dict(metadata) if isinstance(metadata, dict) else {}
            identifiers = normalized.get("identifiers", {})
            identifiers = dict(identifiers) if isinstance(identifiers, dict) else {}

            provider_document_id = str(
                identifiers.get("documentId")
                or normalized.get("documentId")
                or metadata.get("providerDocumentId")
                or ""
            )
            provider_chunk_id = str(
                identifiers.get("chunkId")
                or normalized.get("chunkId")
                or metadata.get("providerChunkId")
                or ""
            )
            document = document_by_provider_id.get(provider_document_id)
            chunk = chunk_by_provider_id.get(provider_chunk_id)

            if document:
                normalized["documentId"] = document.id
                metadata.setdefault("fileName", document.file_name)
                metadata.setdefault("goalId", document.goal_id)
                metadata.setdefault(
                    "goalIds",
                    [
                        link.goal_id
                        for link in self._knowledge_repository.list_document_goal_links(
                            query.user_id, document_id=document.id
                        )
                    ],
                )
                metadata.setdefault("subject", document.subject)
                metadata.setdefault("topic", document.topic)
                metadata["providerDocumentId"] = provider_document_id
                identifiers["documentId"] = document.id
                identifiers["providerDocumentId"] = provider_document_id
            if chunk:
                normalized["chunkId"] = chunk.id
                metadata["providerChunkId"] = provider_chunk_id
                identifiers["chunkId"] = chunk.id
                identifiers["providerChunkId"] = provider_chunk_id
            elif provider_chunk_id:
                metadata["providerChunkId"] = provider_chunk_id
                identifiers["providerChunkId"] = provider_chunk_id

            normalized["metadata"] = metadata
            normalized["identifiers"] = identifiers
            normalized_results.append(normalized)
        return {
            "query": str(provider_result.get("query") or query.query),
            "results": normalized_results,
        }

    def _prepare_chunk_embedding(self, *, user_id: str, chunk) -> ChunkEmbeddingRecord:
        embedding = self._embedding_provider.embed(chunk.content)
        record = self._repository.get_record_for_chunk(user_id=user_id, chunk_id=chunk.id)
        if record is None:
            record = ChunkEmbeddingRecord(
                user_id=user_id,
                document_id=chunk.document_id,
                chunk_id=chunk.id,
                embedding_provider=embedding.provider,
                embedding_model=embedding.model,
                embedding_dimension=embedding.dimension,
            )
        vector_ref = f"chunk:{chunk.id}"
        self._vector_store.upsert(
            vector_ref=vector_ref,
            vector=embedding.vector,
            payload={
                "userId": user_id,
                "documentId": chunk.document_id,
                "chunkId": chunk.id,
                "content": chunk.content,
                "metadata": chunk.metadata,
                "goalId": chunk.metadata.get("goalId"),
                "planetType": chunk.metadata.get("planetType", "study"),
            },
        )
        record.embedding_provider = embedding.provider
        record.embedding_model = embedding.model
        record.embedding_dimension = embedding.dimension
        record.embedding_status = EmbeddingStatus.EMBEDDED
        record.embedding_ref = vector_ref
        record.error_message = None
        record.updated_at = local_now()
        return self._repository.save_record(record)
