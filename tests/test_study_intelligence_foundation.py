import inspect
import unittest
from datetime import timedelta

from backend.app.ai.agent_manager import AgentManager
from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_now, local_today
from backend.app.planet_engine import create_default_registry
from backend.app.planets.study.analytics import StudyAnalyticsService
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
                    "documentId": "doc-analytics",
                    "chunkId": "chunk-analytics",
                    "content": "Analytics grounding chunk.",
                    "metadata": {"subject": "math", "topic": "functions"},
                    "score": 0.91,
                    "identifiers": {
                        "embeddingRef": "chunk:analytics",
                        "documentId": "doc-analytics",
                        "chunkId": "chunk-analytics",
                    },
                }
            ],
        }


class StudyIntelligenceFoundationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _create_goal_plan_and_session(self):
        goal = self.api.create_goal(
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
        plan = self.api.create_plan({"startDate": local_today().isoformat()})
        task = plan["dailyTasks"][0]
        self.api.complete_task(task["id"])
        start = local_now().replace(second=0, microsecond=0)
        session = self.api.start_session(
            {
                "taskId": task["id"],
                "startTime": start.isoformat(),
            }
        )
        self.api.finish_session(
            session["id"],
            {
                "endTime": (start + timedelta(minutes=30)).isoformat(),
            },
        )
        return goal, plan, task

    def test_analyst_capability_is_registered_on_study_agent(self):
        definition = self.api.ai_core.agent_manager.resolve(
            agent_id="study",
            capability="analyst",
        )

        self.assertEqual(definition.agent_id, "study")
        self.assertIn("analyst", definition.capabilities)
        self.assertEqual(definition.prompt_key, "study.analyst.report")

    def test_progress_metrics_are_calculated_from_study_data(self):
        self._create_goal_plan_and_session()

        analytics = self.api.get_study_analytics()

        self.assertEqual(analytics["progressSummary"]["totalTasks"], 7)
        self.assertEqual(analytics["progressSummary"]["completedTasks"], 1)
        self.assertEqual(analytics["progressSummary"]["totalStudyMinutes"], 30)
        self.assertEqual(analytics["progressSummary"]["finishedSessions"], 1)

    def test_insufficient_data_state_without_goal(self):
        analytics = self.api.get_study_analytics()

        self.assertEqual(analytics["dataQuality"]["state"], "insufficient")
        self.assertIn("No active Goal exists.", analytics["dataQuality"]["limitations"])
        self.assertEqual(analytics["progressSummary"]["totalTasks"], 0)

    def test_memory_context_is_included_in_analyst_report(self):
        self._create_goal_plan_and_session()
        self.api.create_memory(
            {
                "scope": "planet",
                "planetType": "study",
                "key": "study_style",
                "value": {"value": "short daily reviews"},
            }
        )

        report = self.api.create_study_analytics_report()

        self.assertTrue(
            any("memory item" in insight for insight in report["learningInsights"])
        )
        self.assertEqual(report["dataQuality"]["state"], "ready")

    def test_retrieval_goes_through_tool_router_for_report(self):
        self._create_goal_plan_and_session()
        spy_tool = SpyRetrieverTool()
        self.api.tool_router.register(spy_tool)

        report = self.api.create_study_analytics_report()

        self.assertEqual(len(spy_tool.invocations), 1)
        self.assertIn("Study analytics", spy_tool.invocations[0]["query"])
        self.assertTrue(report["report"]["retrievalInvoked"])
        self.assertEqual(report["report"]["groundingChunks"][0]["chunkId"], "chunk-analytics")

    def test_structured_report_output_and_no_automatic_behavior(self):
        self._create_goal_plan_and_session()

        report = self.api.create_study_analytics_report()

        self.assertEqual(
            set(report.keys()),
            {
                "progressSummary",
                "learningInsights",
                "weakAreas",
                "recommendedActions",
                "report",
                "dataQuality",
            },
        )
        self.assertEqual(report["report"].get("actionsApplied", []), [])
        source = inspect.getsource(StudyAnalyticsService).lower()
        self.assertNotIn("personality", source)
        self.assertNotIn("psychological", source)

    def test_no_new_planet_or_ai_system_is_created(self):
        planets = create_default_registry().list_planets()

        self.assertEqual(len(planets), 5)
        self.assertNotIn("AICoreService(", inspect.getsource(StudyAnalyticsService))
        self.assertNotIn("AnalystService(", inspect.getsource(AgentManager))

    def test_tutor_behavior_still_works(self):
        self._create_goal_plan_and_session()

        response = self.api.ask_study_tutor({"question": "What should I study?"})

        self.assertIn("answer", response)
        self.assertIn("relatedLearningEvent", response)
        self.assertNotIn("StudyAnalyticsService", inspect.getsource(TutorService))

    def test_milestone_6_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("GET", "/api/study/analytics"), contracts)
        self.assertIn(("POST", "/api/study/analytics/report"), contracts)


if __name__ == "__main__":
    unittest.main()
