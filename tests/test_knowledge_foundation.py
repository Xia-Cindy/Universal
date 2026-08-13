import unittest

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.files import FileService, UnsupportedFileTypeError
from backend.app.knowledge import KnowledgeService
from backend.app.knowledge.repository import KnowledgeRepository


class KnowledgeFoundationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _document_payload(self, **overrides):
        payload = {
            "fileName": "algebra-notes.md",
            "fileType": "markdown",
            "subject": "math",
            "topic": "functions",
            "content": "# Functions\n\nA function maps each input to one output.",
        }
        payload.update(overrides)
        return payload

    def test_document_creation_defaults_to_uploaded_status(self):
        document = self.api.create_knowledge_document(self._document_payload())

        self.assertEqual(document["fileName"], "algebra-notes.md")
        self.assertEqual(document["fileType"], "markdown")
        self.assertEqual(document["planetType"], "study")
        self.assertEqual(document["tags"], [])
        self.assertEqual(document["processingStatus"], "uploaded")
        self.assertIsNone(document["errorMessage"])

    def test_document_creation_supports_work_tech_stack_and_tags(self):
        document = self.api.create_knowledge_document(
            self._document_payload(
                planetType="work",
                techStackId="stack-1",
                tags=["interview", "jd"],
            )
        )

        self.assertEqual(document["planetType"], "work")
        self.assertEqual(document["techStackId"], "stack-1")
        self.assertEqual(document["tags"], ["interview", "jd"])

    def test_file_validation_rejects_unsupported_types(self):
        service = KnowledgeService(repository=KnowledgeRepository(), file_service=FileService())

        with self.assertRaises(UnsupportedFileTypeError):
            service.create_document(
                "local-user",
                self._document_payload(fileName="slides.pptx", fileType="pptx"),
            )

    def test_text_processing_creates_chunks_and_processed_status(self):
        document = self.api.create_knowledge_document(
            self._document_payload(content="Line one.\n\nLine two.\nLine three.")
        )

        detail = self.api.process_knowledge_document(document["id"])

        self.assertEqual(detail["document"]["processingStatus"], "processed")
        self.assertGreaterEqual(len(detail["chunks"]), 1)
        self.assertEqual(detail["chunks"][0]["chunkIndex"], 0)
        self.assertIn("Line one", detail["chunks"][0]["content"])

    def test_processing_status_transitions_to_failed_for_pdf_without_parser(self):
        document = self.api.create_knowledge_document(
            self._document_payload(fileName="reference.pdf", fileType="pdf", content="")
        )

        detail = self.api.process_knowledge_document(document["id"])

        self.assertEqual(detail["document"]["processingStatus"], "failed")
        self.assertIn("PDF parsing is not available yet", detail["document"]["errorMessage"])
        self.assertEqual(detail["chunks"], [])

    def test_document_listing_supports_subject_and_topic_filters(self):
        self.api.create_knowledge_document(self._document_payload(subject="math", topic="functions"))
        self.api.create_knowledge_document(
            self._document_payload(fileName="english.txt", fileType="txt", subject="english", topic="reading")
        )

        math_documents = self.api.list_knowledge_documents(subject="math")
        reading_documents = self.api.list_knowledge_documents(topic="reading")

        self.assertEqual(len(math_documents), 1)
        self.assertEqual(math_documents[0]["subject"], "math")
        self.assertEqual(len(reading_documents), 1)
        self.assertEqual(reading_documents[0]["topic"], "reading")

    def test_document_detail_returns_chunks_after_processing(self):
        document = self.api.create_knowledge_document(
            self._document_payload(content="a " * 900)
        )
        self.api.process_knowledge_document(document["id"])

        detail = self.api.get_knowledge_document(document["id"])

        self.assertEqual(detail["document"]["id"], document["id"])
        self.assertGreater(len(detail["chunks"]), 1)
        self.assertEqual(
            [chunk["chunkIndex"] for chunk in detail["chunks"]],
            list(range(len(detail["chunks"]))),
        )

    def test_overview_returns_status_counts_and_subjects(self):
        document = self.api.create_knowledge_document(self._document_payload())
        self.api.process_knowledge_document(document["id"])

        overview = self.api.knowledge_overview()

        self.assertEqual(overview["statusCounts"]["processed"], 1)
        self.assertEqual(overview["subjects"], [{"subject": "math", "topics": ["functions"]}])

    def test_milestone_4_1_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("POST", "/api/study/knowledge/documents"), contracts)
        self.assertIn(("POST", "/api/study/knowledge/documents/adopt-ragflow"), contracts)
        self.assertIn(("GET", "/api/study/knowledge"), contracts)
        self.assertIn(("GET", "/api/study/knowledge/documents"), contracts)
        self.assertIn(("GET", "/api/study/knowledge/documents/{document_id}"), contracts)
        self.assertIn(("POST", "/api/study/knowledge/documents/{document_id}/process"), contracts)
        self.assertIn(("PATCH", "/api/study/knowledge/documents/{document_id}"), contracts)


if __name__ == "__main__":
    unittest.main()
