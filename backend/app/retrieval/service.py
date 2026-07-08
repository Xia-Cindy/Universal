from backend.app.core.dates import local_now
from backend.app.knowledge.repository import KnowledgeRepository
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
    ) -> None:
        self._knowledge_repository = knowledge_repository
        self._repository = repository or RetrievalRepository()
        self._embedding_provider = embedding_provider or DeterministicEmbeddingProvider()
        self._vector_store = vector_store or InMemoryVectorStore()

    def prepare_document_embeddings(self, user_id: str, document_id: str) -> dict[str, object]:
        document = self._knowledge_repository.get_document(document_id, user_id)
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
        embedding = self._embedding_provider.embed(query.query)
        filters = {"userId": query.user_id}
        if query.document_id:
            filters["documentId"] = query.document_id
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

