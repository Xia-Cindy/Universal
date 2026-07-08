import inspect
import unittest

from backend.app.ai import AICoreService, AIContext, AIRequest, AgentDefinition
from backend.app.api.routes import ApiFacade
from backend.app.planets.study.tutor.service import TutorService


class SpyRetrieverTool:
    name = "retrieval.search"

    def __init__(self) -> None:
        self.invocations: list[dict] = []

    def invoke(self, payload: dict) -> dict:
        self.invocations.append(payload)
        return {
            "query": payload["query"],
            "results": [
                {
                    "documentId": "doc-spy",
                    "chunkId": "chunk-spy",
                    "content": "Spy chunk content about functions.",
                    "metadata": {"subject": "math", "topic": "functions"},
                    "score": 0.99,
                    "identifiers": {
                        "embeddingRef": "chunk:spy",
                        "documentId": "doc-spy",
                        "chunkId": "chunk-spy",
                    },
                }
            ],
        }


class EmptyRetrieverTool:
    name = "retrieval.search"

    def invoke(self, payload: dict) -> dict:
        return {
            "query": payload["query"],
            "results": [],
        }


class DummyContextProvider:
    def build(self, payload: dict) -> AIContext:
        return AIContext(
            {
                "responseHints": {
                    "answer": "Future answer",
                    "reasoning": "Future reasoning",
                    "suggestedNextAction": "Future action",
                    "metadata": {"toolResults": payload.get("toolResults", {})},
                }
            }
        )


class DummyTool:
    name = "future.lookup"

    def invoke(self, payload: dict) -> dict:
        return {"results": [{"value": payload["value"]}]}


class TutorRetrievalIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _processed_document_with_embeddings(self):
        document = self.api.create_knowledge_document(
            {
                "fileName": "functions.md",
                "fileType": "markdown",
                "subject": "math",
                "topic": "functions",
                "content": "A function maps each input to exactly one output.",
            }
        )
        self.api.process_knowledge_document(document["id"])
        self.api.prepare_document_embeddings(document["id"])
        return document

    def test_tutor_retrieval_goes_through_tool_router(self):
        spy_tool = SpyRetrieverTool()
        self.api.tool_router.register(spy_tool)

        response = self.api.ask_study_tutor({"question": "Explain functions"})

        self.assertEqual(len(spy_tool.invocations), 1)
        self.assertEqual(spy_tool.invocations[0]["query"], "Explain functions")
        self.assertTrue(response["retrievalInvoked"])
        self.assertTrue(response["knowledgeSourcesAvailable"])
        self.assertEqual(response["groundingChunks"][0]["chunkId"], "chunk-spy")

    def test_tutor_does_not_call_retrieval_service_directly(self):
        spy_tool = SpyRetrieverTool()
        self.api.tool_router.register(spy_tool)

        def fail(*args, **kwargs):
            raise AssertionError("Tutor must not call RetrievalService directly")

        self.api.retrieval.search = fail
        response = self.api.ask_study_tutor({"question": "Use knowledge"})

        self.assertEqual(len(spy_tool.invocations), 1)
        self.assertIn("Spy chunk content", response["answer"])
        self.assertNotIn("RetrievalService", inspect.getsource(TutorService))

    def test_no_retrieval_results_still_produces_valid_tutor_response(self):
        self.api.tool_router.register(EmptyRetrieverTool())

        response = self.api.ask_study_tutor({"question": "What should I study?"})

        self.assertIn("answer", response)
        self.assertIn("reasoning", response)
        self.assertIn("suggestedNextAction", response)
        self.assertFalse(response["knowledgeSourcesAvailable"])
        self.assertEqual(response["groundingChunks"], [])
        self.assertIn("unavailable", response["sourceNotice"])

    def test_grounded_response_includes_chunk_metadata_and_learning_event(self):
        document = self._processed_document_with_embeddings()

        response = self.api.ask_study_tutor({"question": "What is a function?"})
        event = response["relatedLearningEvent"]

        self.assertTrue(response["retrievalInvoked"])
        self.assertTrue(response["knowledgeSourcesAvailable"])
        self.assertEqual(response["groundingChunks"][0]["documentId"], document["id"])
        self.assertEqual(response["groundingChunks"][0]["metadata"]["topic"], "functions")
        self.assertEqual(event["metadata"]["retrievalInvoked"], True)
        self.assertEqual(event["metadata"]["knowledgeSourcesAvailable"], True)
        self.assertEqual(
            event["metadata"]["groundingChunkIds"],
            [response["groundingChunks"][0]["chunkId"]],
        )
        self.assertFalse(event["metadata"]["ragInvoked"])

    def test_ai_core_tool_invocation_remains_generic(self):
        ai_core = AICoreService()
        ai_core.agent_manager.register(
            AgentDefinition(
                agent_id="future",
                capabilities=("lookup",),
                prompt_key="future.lookup.answer",
                context_builder="future.lookup",
                allowed_tools=("future.lookup",),
            )
        )
        ai_core.prompt_manager.register("future.lookup.answer", "Future prompt")
        ai_core.context_manager.register_provider("future.lookup", DummyContextProvider())
        ai_core.tool_router.register(DummyTool())

        response = ai_core.run(
            AIRequest(
                agent_id="future",
                capability="lookup",
                user_question="Can tools work generically?",
                context_payload={},
                tool_payloads={"future.lookup": {"value": "generic"}},
            )
        )

        self.assertEqual(
            response.metadata["toolResults"]["future.lookup"]["results"][0]["value"],
            "generic",
        )


if __name__ == "__main__":
    unittest.main()
