import unittest

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.retrieval import DeterministicEmbeddingProvider, InMemoryVectorStore, RetrievalQuery


class RetrievalFoundationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _processed_document(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "algebra.md",
                "fileType": "markdown",
                "subject": "math",
                "topic": "functions",
                "content": "Functions map inputs to outputs.\n\nQuadratic functions form parabolas.",
            }
        )
        self.api.process_knowledge_document(document["id"])
        return document

    def test_embedding_provider_is_deterministic(self):
        provider = DeterministicEmbeddingProvider()

        first = provider.embed("same chunk content").vector
        second = provider.embed("same chunk content").vector
        different = provider.embed("different chunk content").vector

        self.assertEqual(first, second)
        self.assertNotEqual(first, different)
        self.assertEqual(len(first), 8)

    def test_vector_store_abstraction_returns_ranked_matches(self):
        provider = DeterministicEmbeddingProvider()
        store = InMemoryVectorStore()
        vector = provider.embed("functions map inputs").vector
        store.upsert(
            vector_ref="chunk:one",
            vector=vector,
            payload={
                "userId": "local-user",
                "documentId": "doc-1",
                "chunkId": "chunk-1",
                "content": "functions map inputs",
                "metadata": {"subject": "math"},
            },
        )

        matches = store.search(query_vector=vector, limit=1, filters={"userId": "local-user"})

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].vector_ref, "chunk:one")
        self.assertEqual(matches[0].score, 1.0)

    def test_chunk_embedding_pipeline_prepares_records(self):
        document = self._processed_document()

        result = self.api.prepare_document_embeddings(document["id"])
        records = self.api.list_document_embeddings(document["id"])

        self.assertEqual(result["status"], "prepared")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["embeddingStatus"], "embedded")
        self.assertEqual(records[0]["embeddingProvider"], "deterministic")
        self.assertTrue(records[0]["embeddingRef"].startswith("chunk:"))

    def test_embedding_preparation_does_not_duplicate_records(self):
        document = self._processed_document()

        self.api.prepare_document_embeddings(document["id"])
        self.api.prepare_document_embeddings(document["id"])
        records = self.api.list_document_embeddings(document["id"])

        self.assertEqual(len(records), 1)

    def test_unprocessed_document_is_not_ready_for_embeddings(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "draft.txt",
                "fileType": "txt",
                "subject": "math",
                "topic": "draft",
                "content": "not processed yet",
            }
        )

        result = self.api.prepare_document_embeddings(document["id"])

        self.assertEqual(result["status"], "not_ready")
        self.assertEqual(result["records"], [])

    def test_retrieval_service_returns_chunks_only(self):
        document = self._processed_document()
        self.api.prepare_document_embeddings(document["id"])

        result = self.api.search_knowledge_chunks(
            {
                "query": "Functions map inputs to outputs.",
                "limit": 2,
                "documentId": document["id"],
            }
        )

        self.assertEqual(result["query"], "Functions map inputs to outputs.")
        self.assertEqual(len(result["results"]), 1)
        chunk = result["results"][0]
        self.assertEqual(
            set(chunk.keys()),
            {"documentId", "chunkId", "content", "metadata", "score", "identifiers"},
        )
        self.assertIn("Functions", chunk["content"])
        self.assertNotIn("answer", result)
        self.assertNotIn("citations", result)
        self.assertNotIn("sources", result)

    def test_search_does_not_invoke_ai_core_or_tutor(self):
        document = self._processed_document()
        self.api.prepare_document_embeddings(document["id"])

        def fail(*args, **kwargs):
            raise AssertionError("Retrieval search must not invoke AI Core or Tutor")

        self.api.ai_core.run = fail
        self.api.study_tutor.ask = fail
        self.api.search_knowledge_chunks({"query": "functions", "limit": 1})

        self.assertEqual(self.api.get_tutor_history(), [])

    def test_retrieval_service_can_be_used_without_api_facade(self):
        document = self._processed_document()
        self.api.retrieval.prepare_document_embeddings("local-user", document["id"])

        result = self.api.retrieval.search(
            RetrievalQuery(user_id="local-user", query="Quadratic functions", limit=1)
        )

        self.assertEqual(len(result["results"]), 1)
        self.assertIn("chunkId", result["results"][0])

    def test_milestone_4_2_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(
            ("POST", "/api/study/knowledge/documents/{document_id}/embeddings/prepare"),
            contracts,
        )
        self.assertIn(
            ("GET", "/api/study/knowledge/documents/{document_id}/embeddings"),
            contracts,
        )
        self.assertIn(("POST", "/api/study/knowledge/retrieval/search"), contracts)


if __name__ == "__main__":
    unittest.main()
