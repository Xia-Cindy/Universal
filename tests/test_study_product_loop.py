import inspect
import json
import unittest
from datetime import timedelta

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_now, local_today
from backend.app.planet_engine import create_default_registry
from backend.app.planets.study.execution import StudyExecutionService
from backend.app.planets.study.onboarding import StudyOnboardingService


class StudyProductLoopTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _goal_payload(self):
        return {
            "goalName": "Graduate math sprint",
            "examName": "Graduate Exam",
            "targetDirection": "quantitative reasoning",
            "deadline": (local_today() + timedelta(days=90)).isoformat(),
            "dailyAvailableMinutes": 50,
            "subjects": ["math", "logic"],
            "currentLevel": "foundation",
            "priority": "high",
        }

    def _create_onboarded_goal(self):
        return self.api.create_onboarding_goal(self._goal_payload())["activeGoal"]

    def _create_plan(self):
        self._create_onboarded_goal()
        return self.api.create_plan({"startDate": local_today().isoformat()})

    def test_new_user_without_goal_sees_onboarding_state(self):
        onboarding = self.api.get_study_onboarding()
        home = self.api.get_study_home()

        self.assertEqual(onboarding["state"], "needs_onboarding")
        self.assertIsNone(onboarding["activeGoal"])
        self.assertEqual(home["state"], "empty")
        self.assertEqual(home["primaryNextAction"]["route"], "/study/goals/new")

    def test_user_creates_goal_through_onboarding(self):
        onboarding = self.api.create_onboarding_goal(self._goal_payload())
        memories = self.api.list_memory(scope="planet", planet_type="study", include_inactive=False)

        self.assertEqual(onboarding["state"], "ready")
        self.assertEqual(onboarding["activeGoal"]["goalName"], "Graduate math sprint")
        self.assertTrue(any(memory["key"] == "target_direction" for memory in memories))
        self.assertTrue(any(memory["key"] == "study_preference" for memory in memories))

    def test_user_creates_plan_and_sees_today_tasks(self):
        plan = self._create_plan()
        home = self.api.get_study_home()

        self.assertEqual(len(plan["dailyTasks"]), 7)
        self.assertEqual(home["state"], "ready")
        self.assertEqual(len(home["todayTasks"]), 1)
        self.assertEqual(home["todayTasks"][0]["taskDate"], local_today().isoformat())

    def test_user_completes_task(self):
        plan = self._create_plan()
        task = plan["dailyTasks"][0]

        completed = self.api.complete_task(task["id"])
        home = self.api.get_study_home()

        self.assertEqual(completed["status"], "completed")
        self.assertEqual(home["progressSummary"]["completedTasks"], 1)

    def test_user_starts_and_finishes_study_session_without_double_counting(self):
        plan = self._create_plan()
        task = plan["dailyTasks"][0]
        start = local_now().replace(second=0, microsecond=0)
        started = self.api.start_execution_session(
            {
                "taskId": task["id"],
                "startTime": start.isoformat(),
            }
        )
        finished = self.api.finish_execution_session(
            started["session"]["id"],
            {
                "endTime": (start + timedelta(minutes=30)).isoformat(),
                "notes": "worked through examples",
                "feeling": "focused",
            },
        )
        finished_again = self.api.finish_execution_session(
            started["session"]["id"],
            {"endTime": (start + timedelta(minutes=90)).isoformat()},
        )

        self.assertEqual(started["state"], "active")
        self.assertEqual(finished["state"], "finished")
        self.assertEqual(finished["session"]["durationMinutes"], 30)
        self.assertEqual(finished_again["session"]["durationMinutes"], 30)
        self.assertEqual(self.api.study_repository.get_task(task["id"], "local-user").status.value, "completed")
        self.assertEqual(len(self.api.list_study_records()), 1)
        self.assertEqual(len(self.api.study_repository.list_learning_events("local-user")), 1)

    def test_study_home_progress_updates_after_session_and_task_completion(self):
        plan = self._create_plan()
        task = plan["dailyTasks"][0]
        self.api.complete_task(task["id"])
        start = local_now().replace(second=0, microsecond=0)
        started = self.api.start_execution_session(
            {
                "taskId": task["id"],
                "startTime": start.isoformat(),
            }
        )
        self.api.finish_execution_session(
            started["session"]["id"],
            {"endTime": (start + timedelta(minutes=35)).isoformat()},
        )

        home = self.api.get_study_home()

        self.assertEqual(home["progressSnapshot"]["todayStudyMinutes"], 35)
        self.assertEqual(home["progressSnapshot"]["weekStudyMinutes"], 35)
        self.assertEqual(home["progressSummary"]["completedTasks"], 1)
        self.assertEqual(home["aiInsight"]["dataQuality"]["state"], "ready")

    def test_analytics_insight_integration_uses_existing_analyst(self):
        plan = self._create_plan()
        task = plan["dailyTasks"][0]
        start = local_now().replace(second=0, microsecond=0)
        started = self.api.start_execution_session(
            {
                "taskId": task["id"],
                "startTime": start.isoformat(),
            }
        )
        self.api.finish_execution_session(
            started["session"]["id"],
            {"endTime": (start + timedelta(minutes=20)).isoformat()},
        )

        analytics = self.api.get_study_analytics()
        home = self.api.get_study_home()

        self.assertEqual(home["aiInsight"]["learningInsights"], analytics["learningInsights"])
        self.assertEqual(home["aiInsight"]["recommendedActions"], analytics["recommendedActions"])
        self.assertIn("progressSummary", analytics)

    def test_memory_integration_uses_memory_service_write_points(self):
        plan = self._create_plan()
        task = plan["dailyTasks"][0]
        start = local_now().replace(second=0, microsecond=0)
        started = self.api.start_execution_session(
            {
                "taskId": task["id"],
                "startTime": start.isoformat(),
            }
        )
        self.api.finish_execution_session(
            started["session"]["id"],
            {"endTime": (start + timedelta(minutes=25)).isoformat(), "feeling": "steady"},
        )
        memories = self.api.list_memory(planet_type="study", include_inactive=False)
        onboarding_source = inspect.getsource(StudyOnboardingService)
        execution_source = inspect.getsource(StudyExecutionService)

        self.assertTrue(any(memory["key"] == "recent_learning_activity" for memory in memories))
        self.assertTrue(any(memory["key"] == "study_session_result" for memory in memories))
        self.assertIn("MemoryService", onboarding_source)
        self.assertIn("MemoryService", execution_source)
        self.assertNotIn("MemoryRepository", onboarding_source + execution_source)

    def test_no_ai_core_redesign_or_new_planet(self):
        planets = create_default_registry().list_planets()

        self.assertEqual(len(planets), 5)
        self.assertIs(self.api.study_tutor._ai_core, self.api.ai_core)
        self.assertIs(self.api.study_analytics._ai_core, self.api.ai_core)
        self.assertNotIn("AICoreService", inspect.getsource(StudyExecutionService))
        self.assertNotIn("AICoreService", inspect.getsource(StudyOnboardingService))

    def test_no_hard_coded_demo_content_in_study_home(self):
        self._create_plan()

        home_text = json.dumps(self.api.get_study_home())

        self.assertNotIn("Milestone", home_text)
        self.assertNotIn("placeholder", home_text.lower())
        self.assertNotIn("Knowledge starts", home_text)

    def test_milestone_7_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("GET", "/api/study/onboarding"), contracts)
        self.assertIn(("POST", "/api/study/onboarding/goal"), contracts)
        self.assertIn(("POST", "/api/study/execution/sessions"), contracts)
        self.assertIn(("PATCH", "/api/study/execution/sessions/{session_id}/finish"), contracts)


if __name__ == "__main__":
    unittest.main()
