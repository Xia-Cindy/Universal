import unittest

from backend.app.api.routes import ApiFacade


class CitationEvidenceContractTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def test_tutor_returns_stable_sources_and_scope(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "systems.md",
                "fileType": "markdown",
                "subject": "systems",
                "topic": "memory",
                "content": "A process owns virtual memory.",
            }
        )
        self.api.process_knowledge_document(document["id"])
        self.api.prepare_document_embeddings(document["id"])

        response = self.api.ask_study_tutor({"question": "What is virtual memory?", "scope": "all_study"})

        self.assertEqual(response["scope"], "all_study")
        self.assertEqual(response["sources"][0]["documentId"], document["id"])
        self.assertEqual(response["sources"][0]["quote"], "A process owns virtual memory.")
        self.assertIn("/study/knowledge?documentId=", response["sources"][0]["sourceUrl"])

    def test_no_knowledge_has_explicit_empty_source_state(self):
        response = self.api.ask_study_tutor({"question": "What next?"})

        self.assertEqual(response.get("sources", []), [])
        self.assertFalse(response["knowledgeSourcesAvailable"])
        self.assertIn("unavailable", response["sourceNotice"])

    def test_source_contract_can_be_saved_as_learning_event(self):
        response = self.api.ask_study_tutor({"question": "Summarize my next step"})
        event = self.api.save_tutor_answer_event(
            {
                "question": "Summarize my next step",
                "answer": response["answer"],
                "sources": response.get("sources", []),
            }
        )

        self.assertEqual(event["eventType"], "tutor_answer_saved")
        self.assertEqual(event["metadata"]["sources"], [])

    def test_document_evidence_endpoint_uses_same_source_shape(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "notes.txt",
                "fileType": "txt",
                "subject": "logic",
                "topic": "proof",
                "content": "A proof explains why a claim follows.",
            }
        )
        self.api.process_knowledge_document(document["id"])
        evidence = self.api.get_knowledge_evidence(document["id"])

        self.assertEqual(evidence[0]["documentId"], document["id"])
        self.assertEqual(evidence[0]["title"], "notes.txt")
        self.assertIn("sourceId", evidence[0])


if __name__ == "__main__":
    unittest.main()
