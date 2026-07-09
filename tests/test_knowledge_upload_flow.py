import unittest

from backend.app.api.routes import ApiFacade


class KnowledgeUploadFlowTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def test_txt_upload_and_processing_flow(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "systems.txt",
                "fileType": "txt",
                "subject": "computer systems",
                "topic": "memory hierarchy",
                "content": "Cache locality matters.\nMemory hierarchy affects performance.",
            }
        )
        detail = self.api.process_knowledge_document(document["id"])

        self.assertEqual(document["processingStatus"], "uploaded")
        self.assertEqual(detail["document"]["processingStatus"], "processed")
        self.assertGreaterEqual(len(detail["chunks"]), 1)

    def test_markdown_upload_and_processing_flow(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "ai-engineering.md",
                "fileType": "markdown",
                "subject": "AI engineering",
                "topic": "evaluation",
                "content": "# Evaluation\n\nUse tests and task-specific acceptance criteria.",
            }
        )
        detail = self.api.process_knowledge_document(document["id"])

        self.assertEqual(detail["document"]["processingStatus"], "processed")
        self.assertIn("Evaluation", detail["chunks"][0]["content"])

    def test_pdf_metadata_upload_is_accepted_without_parser(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "research-paper.pdf",
                "fileType": "pdf",
                "subject": "AI research",
                "topic": "paper reading",
                "content": "",
            }
        )
        overview = self.api.knowledge_overview()

        self.assertEqual(document["fileType"], "pdf")
        self.assertEqual(document["processingStatus"], "uploaded")
        self.assertEqual(overview["statusCounts"]["uploaded"], 1)

    def test_pdf_processing_failure_preserves_document_record(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "metadata-only.pdf",
                "fileType": "pdf",
                "subject": "systems",
                "topic": "paper",
                "content": "",
            }
        )
        detail = self.api.process_knowledge_document(document["id"])

        self.assertEqual(detail["document"]["processingStatus"], "failed")
        self.assertIn("PDF metadata is accepted", detail["document"]["errorMessage"])


if __name__ == "__main__":
    unittest.main()
