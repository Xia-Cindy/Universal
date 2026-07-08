from backend.app.retrieval.models import ChunkEmbeddingRecord


class RetrievalRepository:
    def __init__(self) -> None:
        self.records: dict[str, ChunkEmbeddingRecord] = {}

    def save_record(self, record: ChunkEmbeddingRecord) -> ChunkEmbeddingRecord:
        self.records[record.id] = record
        return record

    def get_record_for_chunk(
        self,
        *,
        user_id: str,
        chunk_id: str,
    ) -> ChunkEmbeddingRecord | None:
        for record in self.records.values():
            if record.user_id == user_id and record.chunk_id == chunk_id:
                return record
        return None

    def list_records(
        self,
        *,
        user_id: str,
        document_id: str | None = None,
    ) -> list[ChunkEmbeddingRecord]:
        records = [record for record in self.records.values() if record.user_id == user_id]
        if document_id:
            records = [record for record in records if record.document_id == document_id]
        return sorted(records, key=lambda record: record.created_at)

