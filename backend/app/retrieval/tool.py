from backend.app.retrieval.models import RetrievalQuery
from backend.app.retrieval.service import RetrievalService


class RetrieverTool:
    name = "retrieval.search"

    def __init__(self, service: RetrievalService) -> None:
        self._service = service

    def invoke(self, payload: dict) -> dict:
        result = self._service.search(
            RetrievalQuery(
                user_id=payload["userId"],
                query=payload["query"],
                limit=payload.get("limit", 5),
                document_id=payload.get("documentId"),
            )
        )
        return {
            "query": result["query"],
            "results": result["results"],
        }
