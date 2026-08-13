from typing import Protocol

from backend.app.models import Document


class KnowledgeProvider(Protocol):
    name: str

    def health_check(self) -> dict[str, object]:
        ...

    def runtime_probe(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
    ) -> dict[str, object]:
        """Run a provider-owned, non-mutating embedding/retrieval acceptance probe."""
        ...

    def upload_document(self, *, user_id: str, document: Document) -> dict[str, object]:
        ...

    def parse_document(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
    ) -> dict[str, object]:
        ...

    def get_document_status(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
    ) -> dict[str, object]:
        ...

    def delete_document(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
    ) -> dict[str, object]:
        ...

    def list_document_chunks(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
        limit: int = 30,
    ) -> list[dict[str, object]]:
        ...

    def search(
        self,
        *,
        user_id: str,
        query: str,
        dataset_ids: list[str],
        document_ids: list[str] | None = None,
        limit: int = 5,
    ) -> dict[str, object]:
        ...
