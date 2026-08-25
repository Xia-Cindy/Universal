import unittest

from backend.app.ai.llm_gateway import OpenAICompatibleLLMGateway
from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


class WorkAIExplorationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()
        self.stack = self.api.create_work_tech_stack(
            {"name": "Docker", "category": "Runtime", "proficiency": "learning"}
        )
        self.article = self.api.create_work_article(
            self.stack["id"],
            {
                "title": "Socket boundary",
                "articleType": "extension",
                "content": "Do not mount the Docker Socket into a low-trust learning container.",
            },
        )

    def test_selected_passage_uses_shared_ai_core_without_ungranted_knowledge(self):
        response = self.api.ask_work_exploration(
            self.stack["id"],
            {
                "sourceArticleId": self.article["id"],
                "selectedQuote": "Do not mount the Docker Socket into a low-trust learning container.",
                "question": "Why is a Docker Socket dangerous here?",
            },
        )

        self.assertIn("Docker", response["answer"])
        self.assertEqual(response["sourceArticleId"], self.article["id"])
        self.assertFalse(response["knowledgeSourcesAvailable"])
        self.assertEqual(response["sources"], [])
        self.assertIn("没有匹配", response["sourceNotice"])

    def test_saved_exploration_keeps_question_quote_and_sources_without_becoming_practice(self):
        exploration = self.api.create_work_article(
            self.stack["id"],
            {
                "title": "AI exploration: Socket boundary",
                "articleType": "exploration",
                "content": "A Docker Socket can grant control over the daemon.",
                "sourceArticleId": self.article["id"],
                "selectedQuote": "Do not mount the Docker Socket",
                "aiQuestion": "Why is this dangerous?",
                "sources": [{"sourceId": "doc:chunk", "title": "Docker hardening", "quote": "..."}],
            },
        )
        detail = self.api.get_work_tech_stack(self.stack["id"])

        self.assertEqual(exploration["articleType"], "exploration")
        self.assertEqual(exploration["sourceArticleId"], self.article["id"])
        self.assertEqual(exploration["selectedQuote"], "Do not mount the Docker Socket")
        self.assertEqual(exploration["sources"][0]["sourceId"], "doc:chunk")
        self.assertEqual(detail["learningRecords"], [])

    def test_selected_article_must_belong_to_the_current_tech_stack(self):
        other = self.api.create_work_tech_stack(
            {"name": "PostgreSQL", "category": "Data", "proficiency": "learning"}
        )
        other_article = self.api.create_work_article(
            other["id"], {"title": "Isolation", "content": "Transactions isolate writes."}
        )

        with self.assertRaises(ValueError):
            self.api.ask_work_exploration(
                self.stack["id"],
                {"sourceArticleId": other_article["id"], "question": "Explain this."},
            )

    def test_openai_compatible_gateway_requires_all_server_only_configuration(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleLLMGateway(base_url="", api_key="key", model="model")

    def test_ai_exploration_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("GET", "/api/ai/status"), contracts)
        self.assertIn(("POST", "/api/work/tech-stacks/{tech_stack_id}/explorations"), contracts)


if __name__ == "__main__":
    unittest.main()
