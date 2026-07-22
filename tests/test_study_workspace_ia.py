import unittest
from pathlib import Path

from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_today


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StudyWorkspaceIATests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _goal_payload(self, name: str):
        return {
            "goalType": "learning",
            "goalName": name,
            "deadline": None,
            "description": f"{name} description",
            "subjects": [name],
            "currentLevel": "foundation",
            "dailyAvailableMinutes": 45,
            "priority": "medium",
        }

    def test_workspace_returns_current_goal_and_plan_summary(self):
        goal = self.api.create_goal(self._goal_payload("Learn Systems"))
        self.api.create_plan({"startDate": local_today().isoformat()})

        workspace = self.api.get_study_workspace()

        self.assertEqual(workspace["currentGoal"]["id"], goal["id"])
        self.assertTrue(workspace["planSummary"]["hasPlan"])
        self.assertEqual(workspace["primaryAction"]["type"], "start_learning")
        self.assertEqual(workspace["planSummary"]["longTermPlanCount"], 1)
        self.assertEqual(workspace["planSummary"]["monthlyPlanCount"], 1)
        self.assertEqual(workspace["planSummary"]["weeklyPlanCount"], 1)
        self.assertEqual(workspace["planSummary"]["dailyTaskCount"], 7)

    def test_home_data_filters_today_tasks_by_current_goal(self):
        first_goal = self.api.create_goal(self._goal_payload("Learn Python"))
        self.api.create_plan({"startDate": local_today().isoformat()})
        second_goal = self.api.create_goal(self._goal_payload("Learn Databases"))
        self.api.create_plan({"startDate": local_today().isoformat()})

        workspace = self.api.get_study_workspace()
        self.api.switch_goal(first_goal["id"])
        switched_workspace = self.api.get_study_workspace()

        self.assertEqual(workspace["currentGoal"]["id"], second_goal["id"])
        self.assertTrue(all(task["goalId"] == second_goal["id"] for task in workspace["todayTasks"]))
        self.assertTrue(all(task["goalId"] == first_goal["id"] for task in switched_workspace["todayTasks"]))

    def test_plan_hierarchy_keeps_tasks_under_goal_and_week(self):
        goal = self.api.create_goal(self._goal_payload("Learn Architecture"))
        workspace_without_plan = self.api.get_study_workspace()
        self.api.create_plan({"startDate": local_today().isoformat()})
        workspace = self.api.get_study_workspace()

        self.assertFalse(workspace_without_plan["planSummary"]["hasPlan"])
        self.assertEqual(workspace_without_plan["primaryAction"]["type"], "create_plan")
        self.assertEqual(workspace["plans"]["longTermPlans"][0]["goalId"], goal["id"])
        self.assertEqual(workspace["plans"]["monthlyPlans"][0]["goalId"], goal["id"])
        self.assertEqual(workspace["plans"]["weeklyPlans"][0]["goalId"], goal["id"])
        self.assertTrue(all(task["goalId"] == goal["id"] for task in workspace["plans"]["dailyTasks"]))
        self.assertTrue(all(task["weekPlanId"] for task in workspace["plans"]["dailyTasks"]))

    def test_navigation_keeps_goals_as_management_entry_not_primary_nav(self):
        source = (PROJECT_ROOT / "frontend/src/planets/study/layout/StudyWorkspace.vue").read_text()
        router_source = (PROJECT_ROOT / "frontend/src/router/index.ts").read_text()
        goals_source = (PROJECT_ROOT / "frontend/src/planets/study/goals/StudyGoals.vue").read_text()

        self.assertIn("Universe Home", source)
        self.assertIn("Current Goal", source)
        self.assertIn("/study/goals", source)
        self.assertIn("goals/new", router_source)
        self.assertIn('to="/study/goals/new"', goals_source)
        self.assertIn("{ label: 'Home', route: '/study' }", source)
        self.assertIn("{ label: 'Plan', route: '/study/plan' }", source)
        self.assertNotIn("{ label: 'Goals', route: '/study/goals' }", source)
        self.assertIn("Universe > Study Planet", source)

    def test_plan_calendar_and_priority_are_user_visible(self):
        source = (PROJECT_ROOT / "frontend/src/planets/study/plan/StudyPlan.vue").read_text()

        self.assertIn("本周任务日历", source)
        self.assertIn("priorityLabel", source)
        self.assertIn("v-model=\"task.priority\"", source)

    def test_existing_study_contracts_remain_compatible(self):
        self.api.create_goal(self._goal_payload("Learn APIs"))
        self.api.create_plan({"startDate": local_today().isoformat()})

        home = self.api.get_study_home()
        workspace = self.api.get_study_workspace()
        analytics = self.api.get_study_analytics()

        self.assertIn("currentGoal", home)
        self.assertIn("currentGoal", workspace)
        self.assertIn("analyticsSummary", workspace)
        self.assertIn("progressSummary", analytics)


if __name__ == "__main__":
    unittest.main()
