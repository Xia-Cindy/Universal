import unittest
from datetime import timedelta

from backend.app.ai import (
    AICoreService,
    AIContext,
    AIRequest,
    AgentDefinition,
    ContextManager,
    PromptManager,
)
from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_today
from backend.app.planets.study.tutor.context_provider import StudyTutorContextProvider


class DummyContextProvider:
    def build(self, payload: dict) -> AIContext:
        return AIContext(
            {
                "responseHints": {
                    "answer": "Dummy answer",
                    "reasoning": "Dummy reasoning",
                    "suggestedNextAction": "Dummy next action",
                    "metadata": {},
                }
            }
        )


class AICoreStudyTutorTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _prepare_learning_context(self):
        self.api.create_goal(
            {
                "goalName": "2027 MEM",
                "examName": "MEM",
                "deadline": (local_today() + timedelta(days=120)).isoformat(),
                "subjects": ["math", "english"],
                "currentLevel": "basic",
                "dailyAvailableMinutes": 45,
                "priority": "high",
            }
        )
        return self.api.create_plan({"startDate": local_today().isoformat()})

    def test_ai_core_context_provider_building_excludes_knowledge_sources(self):
        manager = ContextManager()
        manager.register_provider("study.tutor", StudyTutorContextProvider())
        context = manager.build_context(
            "study.tutor",
            {
                "user": {"id": "local-user", "displayName": "Cindy"},
                "goal": {"goalName": "2027 MEM"},
                "currentPlan": {"yearPlan": {"title": "MEM Learning Plan"}},
                "dailyTasks": [{"subject": "math", "topic": "permutation", "estimatedMinutes": 45}],
                "studySessions": [],
                "learningEvents": [],
            },
        )

        payload = context.to_dict()

        self.assertEqual(payload["user"]["id"], "local-user")
        self.assertEqual(payload["goal"]["goalName"], "2027 MEM")
        self.assertFalse(payload["knowledgeSourcesAvailable"])

    def test_deterministic_provider_behavior(self):
        ai_core = AICoreService()
        ai_core.agent_manager.register(
            AgentDefinition(
                agent_id="study",
                capabilities=("tutor",),
                prompt_key="study.tutor.answer",
                context_builder="study.tutor",
            )
        )
        ai_core.prompt_manager.register("study.tutor.answer", "Study Tutor prompt")
        ai_core.context_manager.register_provider("study.tutor", StudyTutorContextProvider())
        request = AIRequest(
            agent_id="study",
            capability="tutor",
            user_question="What should I study next?",
            context_payload={
                "user": {"id": "local-user", "displayName": "Cindy"},
                "goal": {"goalName": "2027 MEM"},
                "currentPlan": None,
                "dailyTasks": [
                    {
                        "subject": "math",
                        "topic": "permutation",
                        "estimatedMinutes": 45,
                    }
                ],
                "studySessions": [],
                "learningEvents": [],
            },
        )

        first = ai_core.run(request).to_dict()
        second = ai_core.run(request).to_dict()

        self.assertEqual(first, second)
        self.assertIn("permutation", first["suggestedNextAction"])

    def test_future_agent_can_register_without_core_conditionals(self):
        ai_core = AICoreService()
        ai_core.agent_manager.register(
            AgentDefinition(
                agent_id="future",
                capabilities=("coach",),
                prompt_key="future.coach.answer",
                context_builder="future.coach",
            )
        )
        ai_core.prompt_manager.register("future.coach.answer", "Future prompt")
        ai_core.context_manager.register_provider("future.coach", DummyContextProvider())

        response = ai_core.run(
            AIRequest(
                agent_id="future",
                capability="coach",
                user_question="What next?",
                context_payload={},
            )
        )

        self.assertEqual(response.answer, "Dummy answer")

    def test_prompt_manager_resolves_prompt_keys(self):
        prompts = PromptManager()
        prompts.register("study.tutor.answer", "Study Tutor prompt")

        self.assertEqual(prompts.get("study.tutor.answer"), "Study Tutor prompt")

    def test_tutor_request_flow_creates_learning_event(self):
        self._prepare_learning_context()

        response = self.api.ask_study_tutor({"question": "What should I study next?"})
        history = self.api.get_tutor_history()

        self.assertIn("answer", response)
        self.assertIn("reasoning", response)
        self.assertIn("suggestedNextAction", response)
        self.assertIn("relatedLearningEvent", response)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["eventType"], "tutor_interaction")

    def test_tutor_does_not_invoke_rag_or_fake_sources(self):
        self._prepare_learning_context()

        response = self.api.ask_study_tutor({"question": "Explain my next task"})
        event = response["relatedLearningEvent"]

        self.assertFalse(response["knowledgeSourcesAvailable"])
        self.assertIn("unavailable", response["sourceNotice"])
        self.assertNotIn("sources", response)
        self.assertFalse(event["metadata"]["ragInvoked"])
        self.assertFalse(event["metadata"]["knowledgeSourcesAvailable"])

    def test_milestone_3_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("POST", "/api/study/tutor/ask"), contracts)
        self.assertIn(("GET", "/api/study/tutor/history"), contracts)


if __name__ == "__main__":
    unittest.main()
