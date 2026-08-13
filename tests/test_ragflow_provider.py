import unittest
from unittest.mock import patch

from backend.app.knowledge import KnowledgeRepository, KnowledgeService
from backend.app.knowledge.providers import RAGFlowKnowledgeProvider
from backend.app.knowledge.providers.ragflow import RAGFlowAPIError, RAGFlowClient
from backend.app.models import Document, DocumentStatus, DocumentType
from backend.app.retrieval import RetrievalQuery, RetrievalService


class FakeKnowledgeProvider:
    name = "ragflow"

    def __init__(self):
        self.upload_calls = []
        self.parse_calls = []
        self.search_calls = []
        self.document_status = "done"

    def upload_document(self, *, user_id, document):
        self.upload_calls.append({"userId": user_id, "documentId": document.id})
        return {
            "provider": self.name,
            "datasetId": "dataset-1",
            "documentId": "provider-doc-1",
            "status": "uploaded",
        }

    def parse_document(self, *, user_id, dataset_id, document_id):
        self.parse_calls.append({"userId": user_id, "datasetId": dataset_id, "documentId": document_id})
        return {
            "provider": self.name,
            "datasetId": dataset_id,
            "documentId": document_id,
            "status": "parsed",
        }

    def get_document_status(self, *, user_id, dataset_id, document_id):
        return {
            "provider": self.name,
            "datasetId": dataset_id,
            "documentId": document_id,
            "status": self.document_status,
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
    def __init__(self, *, status_run="DONE", fail_reason=None):
        self.requests = []
        self.dataset_counter = 0
        self.status_run = status_run
        self.fail_reason = fail_reason

    def request_json(self, method, path, payload=None, query=None):
        self.requests.append((method, path, payload, query))
        if path == "/api/v1/datasets" and method == "POST":
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
                    "docs": [{"id": "doc-1", "run": self.status_run, "fail_reason": self.fail_reason}],
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
    def test_ragflow_client_normalizes_socket_timeout(self):
        client = RAGFlowClient(base_url="http://ragflow.test", api_key="test", timeout_seconds=1)

        with patch("backend.app.knowledge.providers.ragflow.request.urlopen", side_effect=TimeoutError("timed out")):
            with self.assertRaisesRegex(RAGFlowAPIError, "RAGFlow connection failed: timed out"):
                client.request_json("GET", "/api/v1/datasets")

    def test_upload_timeout_marks_document_failed_with_actionable_message(self):
        class TimeoutProvider(FakeKnowledgeProvider):
            def upload_document(self, *, user_id, document):
                raise RAGFlowAPIError("RAGFlow connection failed: timed out")

        service = KnowledgeService(repository=KnowledgeRepository(), provider=TimeoutProvider())
        document = service.create_document(
            "local-user",
            {
                "fileName": "timed-out.txt",
                "fileType": "txt",
                "subject": "runtime",
                "topic": "timeout",
                "content": "F1 timeout acceptance sample",
            },
        )

        detail = service.process_document("local-user", document.id)

        self.assertEqual(detail["document"]["processingStatus"], "failed")
        self.assertEqual(detail["document"]["providerStatus"], "failed")
        self.assertIn("RAGFlow connection failed: timed out", detail["document"]["errorMessage"])

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

    def test_adopt_existing_ragflow_document_caches_readable_chunks_without_upload_or_parse(self):
        provider = FakeKnowledgeProvider()
        provider.document_status = "running"
        service = KnowledgeService(repository=KnowledgeRepository(), provider=provider)

        detail = service.adopt_ragflow_document(
            "local-user",
            {
                "fileName": "existing.pdf",
                "fileType": "pdf",
                "subject": "data",
                "topic": "governance",
                "providerDatasetId": "dataset-existing",
                "providerDocumentId": "provider-doc-existing",
            },
        )

        self.assertEqual(detail["document"]["providerDatasetId"], "dataset-existing")
        self.assertEqual(detail["document"]["providerDocumentId"], "provider-doc-existing")
        self.assertEqual(detail["document"]["processingStatus"], "chunking")
        self.assertEqual(detail["chunks"][0]["content"], "RAGFlow chunk content")
        self.assertEqual(provider.upload_calls, [])
        self.assertEqual(provider.parse_calls, [])

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
                processing_status=DocumentStatus.PROCESSED,
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

    def test_retrieval_excludes_unprocessed_provider_documents_from_evidence(self):
        provider = FakeKnowledgeProvider()
        repository = KnowledgeRepository()
        repository.save_document(
            Document(
                user_id="local-user",
                file_name="still-indexing.pdf",
                file_type=DocumentType.PDF,
                subject="systems",
                topic="memory",
                provider="ragflow",
                provider_dataset_id="dataset-1",
                provider_document_id="provider-doc-pending",
                processing_status=DocumentStatus.CHUNKING,
            )
        )
        ready = repository.save_document(
            Document(
                user_id="local-user",
                file_name="ready.md",
                file_type=DocumentType.MARKDOWN,
                subject="systems",
                topic="memory",
                provider="ragflow",
                provider_dataset_id="dataset-1",
                provider_document_id="provider-doc-ready",
                processing_status=DocumentStatus.PROCESSED,
            )
        )

        RetrievalService(knowledge_repository=repository, knowledge_provider=provider).search(
            RetrievalQuery(user_id="local-user", query="memory", limit=3)
        )

        self.assertEqual(provider.search_calls[0]["documentIds"], ["provider-doc-ready"])
        self.assertEqual(ready.provider_document_id, "provider-doc-ready")

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
        create_names = [request[2]["name"] for request in client.requests if request[0] == "POST" and request[1] == "/api/v1/datasets"]
        self.assertIn("Study", create_names[0])
        self.assertIn("goal-a", create_names[0])
        dataset_creates = [request for request in client.requests if request[0] == "POST" and request[1] == "/api/v1/datasets"]
        self.assertEqual(len(dataset_creates), 2)
        parser_config = dataset_creates[0][2]["parser_config"]
        self.assertEqual(parser_config["layout_recognize"], "Plain Text")
        self.assertFalse(parser_config["raptor"]["use_raptor"])
        self.assertFalse(parser_config["graphrag"]["use_graphrag"])

    def test_dataset_scope_uses_goal_and_tech_stack_names(self):
        client = StubRAGFlowClient()
        provider = RAGFlowKnowledgeProvider(client=client)
        study_document = Document(
            user_id="local-user", file_name="study.md", file_type=DocumentType.MARKDOWN,
            subject="math", topic="algebra", goal_id="goal-12345678", scope_name="AI 研究生目标", content="content",
        )
        work_document = Document(
            user_id="local-user", file_name="work.md", file_type=DocumentType.MARKDOWN,
            subject="backend", topic="java", planet_type="work", tech_stack_id="stack-12345678",
            scope_name="Java", content="content",
        )
        provider.upload_document(user_id="local-user", document=study_document)
        provider.upload_document(user_id="local-user", document=work_document)
        names = [request[2]["name"] for request in client.requests if request[0] == "POST" and request[1] == "/api/v1/datasets"]
        self.assertEqual(names[0], "Universe OS Knowledge / Study / AI 研究生目标 (goal-123)")
        self.assertEqual(names[1], "Universe OS Knowledge / Work / Java (stack-12)")

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

    def test_running_ragflow_document_exposes_completed_chunks_without_becoming_processed(self):
        provider = RAGFlowKnowledgeProvider(client=StubRAGFlowClient(status_run="RUNNING"))
        repository = KnowledgeRepository()
        document = repository.save_document(
            Document(
                user_id="local-user",
                file_name="long-running.pdf",
                file_type=DocumentType.PDF,
                subject="systems",
                topic="queue",
                provider="ragflow",
                provider_dataset_id="dataset-1",
                provider_document_id="doc-1",
                processing_status=DocumentStatus.CHUNKING,
            )
        )

        detail = KnowledgeService(repository=repository, provider=provider).refresh_document(
            "local-user", document.id
        )

        self.assertEqual(detail["document"]["processingStatus"], "chunking")
        self.assertEqual(detail["document"]["providerStatus"], "running")
        self.assertEqual(detail["chunks"][0]["content"], "Normalized chunk")
        chunk_request = next(
            request for request in provider._client.requests
            if request[0] == "GET" and request[1].endswith("/chunks")
        )
        self.assertEqual(chunk_request[3]["page_size"], 100)

    def test_ragflow_embedding_failure_exposes_actionable_error_code(self):
        client = StubRAGFlowClient(
            status_run="FAIL",
            fail_reason='Fail to bind embedding model: InvalidApiKey / Invalid API-key provided.',
        )
        provider = RAGFlowKnowledgeProvider(client=client)
        repository = KnowledgeRepository()
        document = repository.save_document(
            Document(
                user_id="local-user",
                file_name="failed.pdf",
                file_type=DocumentType.PDF,
                subject="runtime",
                topic="embedding",
                provider="ragflow",
                provider_dataset_id="dataset-1",
                provider_document_id="doc-1",
            )
        )
        detail = KnowledgeService(repository=repository, provider=provider).refresh_document(
            "local-user", document.id
        )

        self.assertEqual(detail["document"]["processingStatus"], "failed")
        self.assertEqual(
            detail["document"]["providerErrorCode"],
            "RAGFLOW_EMBEDDING_INVALID_API_KEY",
        )
        self.assertIn("Check the selected embedding model provider credentials", detail["document"]["errorMessage"])


if __name__ == "__main__":
    unittest.main()
