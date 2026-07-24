import unittest

from backend.app.knowledge import KnowledgeRepository, KnowledgeService
from backend.app.knowledge.providers import RAGFlowKnowledgeProvider
from backend.app.models import Document, DocumentType
from backend.app.retrieval import RetrievalQuery, RetrievalService


class FakeKnowledgeProvider:
    name = "ragflow"

    def __init__(self):
        self.upload_calls = []
        self.search_calls = []

    def upload_document(self, *, user_id, document):
        self.upload_calls.append({"userId": user_id, "documentId": document.id})
        return {
            "provider": self.name,
            "datasetId": "dataset-1",
            "documentId": "provider-doc-1",
            "status": "uploaded",
        }

    def parse_document(self, *, user_id, dataset_id, document_id):
        return {
            "provider": self.name,
            "datasetId": dataset_id,
            "documentId": document_id,
            "status": "parsed",
        }

    def list_document_chunks(self, *, user_id, dataset_id, document_id, limit=30):
        return [
            {
                "chunkId": "provider-chunk-1",
                "content": "RAGFlow chunk content",
                "metadata": {"datasetId": dataset_id, "documentId": document_id},
            }
        ]

    def search(self, *, user_id, query, dataset_ids, document_ids=None, limit=5):
        self.search_calls.append(
            {
                "userId": user_id,
                "query": query,
                "datasetIds": dataset_ids,
                "documentIds": document_ids,
                "limit": limit,
            }
        )
        return {
            "query": query,
            "results": [
                {
                    "documentId": "provider-doc-1",
                    "chunkId": "provider-chunk-1",
                    "content": "RAGFlow retrieval content",
                    "metadata": {"provider": self.name},
                    "score": 0.82,
                    "identifiers": {"provider": self.name, "chunkId": "provider-chunk-1"},
                }
            ],
        }


class StubRAGFlowClient:
    def __init__(self):
        self.requests = []
        self.dataset_counter = 0

    def request_json(self, method, path, payload=None, query=None):
        self.requests.append((method, path, payload, query))
        if path == "/api/v1/datasets":
            self.dataset_counter += 1
            dataset_id = "dataset-created" if self.dataset_counter == 1 else f"dataset-created-{self.dataset_counter}"
            return {"code": 0, "data": {"id": dataset_id}}
        if path.endswith("/chunks") and method == "POST":
            return {"code": 0, "data": {"run": "parsed"}}
        if path.endswith("/chunks") and method == "GET":
            return {
                "code": 0,
                "data": {
                    "chunks": [
                        {
                            "id": "chunk-1",
                            "document_id": "doc-1",
                            "content": "Normalized chunk",
                            "available": True,
                        }
                    ]
                },
            }
        if path.endswith("/documents") and method == "GET":
            return {
                "code": 0,
                "data": {
                    "docs": [{"id": "doc-1", "run": "DONE", "fail_reason": None}],
                    "total": 1,
                },
            }
        if path == "/api/v1/datasets" and method == "GET":
            return {"code": 0, "data": []}
        if path.endswith("/documents") and method == "DELETE":
            return {"code": 0}
        if path == "/api/v1/retrieval":
            return {
                "code": 0,
                "data": {
                    "chunks": [
                        {
                            "id": "chunk-1",
                            "document_id": "doc-1",
                            "dataset_id": "dataset-created",
                            "content": "Retrieved by RAGFlow",
                            "similarity": 0.91,
                        }
                    ]
                },
            }
        return {"code": 0}

    def upload_document(self, *, dataset_id, file_name, content, file_type, content_encoding="text"):
        self.requests.append(("UPLOAD", dataset_id, file_name, file_type))
        return {"code": 0, "data": [{"id": "doc-1", "run": "uploaded"}]}


class RAGFlowProviderTests(unittest.TestCase):
    def test_knowledge_service_processes_document_through_provider(self):
        provider = FakeKnowledgeProvider()
        service = KnowledgeService(repository=KnowledgeRepository(), provider=provider)
        document = service.create_document(
            "local-user",
            {
                "fileName": "logic.md",
                "fileType": "markdown",
                "subject": "logic",
                "topic": "deduction",
                "content": "RAGFlow source content",
            },
        )

        detail = service.process_document("local-user", document.id)

        self.assertEqual(detail["document"]["provider"], "ragflow")
        self.assertEqual(detail["document"]["providerDatasetId"], "dataset-1")
        self.assertEqual(detail["document"]["providerDocumentId"], "provider-doc-1")
        self.assertEqual(detail["document"]["processingStatus"], "processed")
        self.assertEqual(detail["chunks"][0]["metadata"]["providerChunkId"], "provider-chunk-1")

        service.process_document("local-user", document.id)

        self.assertEqual(len(provider.upload_calls), 1)

    def test_retrieval_service_uses_provider_search(self):
        provider = FakeKnowledgeProvider()
        repository = KnowledgeRepository()
        document = repository.save_document(
            Document(
                user_id="local-user",
                file_name="logic.md",
                file_type=DocumentType.MARKDOWN,
                subject="logic",
                topic="deduction",
                provider="ragflow",
                provider_dataset_id="dataset-1",
                provider_document_id="provider-doc-1",
            )
        )
        retrieval = RetrievalService(knowledge_repository=repository, knowledge_provider=provider)

        result = retrieval.search(
            RetrievalQuery(user_id="local-user", query="deduction", limit=3, document_id=document.id)
        )

        self.assertEqual(result["results"][0]["content"], "RAGFlow retrieval content")
        self.assertEqual(result["results"][0]["documentId"], document.id)
        self.assertEqual(result["results"][0]["metadata"]["providerDocumentId"], "provider-doc-1")
        self.assertEqual(provider.search_calls[0]["datasetIds"], ["dataset-1"])
        self.assertEqual(provider.search_calls[0]["documentIds"], ["provider-doc-1"])

    def test_ragflow_adapter_normalizes_api_responses(self):
        client = StubRAGFlowClient()
        provider = RAGFlowKnowledgeProvider(client=client)
        document = Document(
            user_id="local-user",
            file_name="logic.md",
            file_type=DocumentType.MARKDOWN,
            subject="logic",
            topic="deduction",
            content="content",
        )

        upload = provider.upload_document(user_id="local-user", document=document)
        parse = provider.parse_document(
            user_id="local-user",
            dataset_id=upload["datasetId"],
            document_id=upload["documentId"],
        )
        chunks = provider.list_document_chunks(
            user_id="local-user",
            dataset_id=upload["datasetId"],
            document_id=upload["documentId"],
        )
        search = provider.search(
            user_id="local-user",
            query="deduction",
            dataset_ids=[upload["datasetId"]],
            limit=1,
        )

        self.assertEqual(upload["datasetId"], "dataset-created")
        self.assertEqual(upload["documentId"], "doc-1")
        self.assertEqual(parse["status"], "parsed")
        self.assertEqual(chunks[0]["content"], "Normalized chunk")
        self.assertEqual(search["results"][0]["score"], 0.91)

    def test_ragflow_adapter_uses_separate_dataset_per_study_goal(self):
        client = StubRAGFlowClient()
        provider = RAGFlowKnowledgeProvider(client=client)
        first_goal_document = Document(
            user_id="local-user",
            file_name="goal-a.md",
            file_type=DocumentType.MARKDOWN,
            subject="math",
            topic="algebra",
            goal_id="goal-a",
            content="content",
        )
        same_goal_document = Document(
            user_id="local-user",
            file_name="goal-a-2.md",
            file_type=DocumentType.MARKDOWN,
            subject="math",
            topic="functions",
            goal_id="goal-a",
            content="content",
        )
        second_goal_document = Document(
            user_id="local-user",
            file_name="goal-b.md",
            file_type=DocumentType.MARKDOWN,
            subject="english",
            topic="reading",
            goal_id="goal-b",
            content="content",
        )

        first_upload = provider.upload_document(user_id="local-user", document=first_goal_document)
        same_goal_upload = provider.upload_document(user_id="local-user", document=same_goal_document)
        second_upload = provider.upload_document(user_id="local-user", document=second_goal_document)

        self.assertEqual(first_upload["datasetId"], same_goal_upload["datasetId"])
        self.assertNotEqual(first_upload["datasetId"], second_upload["datasetId"])
        dataset_creates = [request for request in client.requests if request[1] == "/api/v1/datasets"]
        self.assertEqual(len(dataset_creates), 2)

    def test_ragflow_runtime_contract_normalizes_health_status_and_delete(self):
        client = StubRAGFlowClient()
        provider = RAGFlowKnowledgeProvider(client=client)

        self.assertEqual(provider.health_check()["status"], "ok")
        status = provider.get_document_status(
            user_id="local-user",
            dataset_id="dataset-1",
            document_id="doc-1",
        )
        self.assertEqual(status["status"], "done")
        deleted = provider.delete_document(
            user_id="local-user",
            dataset_id="dataset-1",
            document_id="doc-1",
        )
        self.assertEqual(deleted["status"], "deleted")


if __name__ == "__main__":
    unittest.main()
