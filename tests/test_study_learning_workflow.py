import unittest
from datetime import timedelta

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.core.dates import local_now, local_today


class StudyLearningWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def _create_goal(self):
        return self.api.create_goal(
            {
                "goalName": "2027 MEM",
                "examName": "MEM",
                "deadline": (local_today() + timedelta(days=120)).isoformat(),
                "subjects": ["math", "english", "logic"],
                "currentLevel": "basic",
                "dailyAvailableMinutes": 45,
                "priority": "high",
            }
        )

    def test_goal_creation_and_active_goal_retrieval(self):
        goal = self._create_goal()
        active = self.api.get_active_goal()

        self.assertEqual(active["id"], goal["id"])
        self.assertEqual(active["goalName"], "2027 MEM")
        self.assertEqual(active["subjects"], ["math", "english", "logic"])

    def test_plan_creation_generates_daily_tasks(self):
        self._create_goal()
        plan = self.api.create_plan({"startDate": local_today().isoformat()})

        self.assertEqual(plan["yearPlan"]["year"], local_today().year)
        self.assertEqual(len(plan["monthPlans"]), 1)
        self.assertEqual(len(plan["weekPlans"]), 1)
        self.assertEqual(len(plan["dailyTasks"]), 7)

    def test_goal_and_plan_hierarchy_can_be_updated(self):
        goal = self._create_goal()
        plan = self.api.create_plan({"startDate": local_today().isoformat()})

        updated_goal = self.api.update_goal(
            goal["id"],
            {
                "goalName": "2027 MEM sprint",
                "subjects": ["logic", "writing"],
                "dailyAvailableMinutes": 60,
            },
        )
        updated_year = self.api.update_year_plan(plan["yearPlan"]["id"], {"title": "MEM annual route"})
        updated_month = self.api.update_month_plan(
            plan["monthPlans"][0]["id"],
            {"title": "Logic month", "focus": "Stabilize logic practice."},
        )
        updated_week = self.api.update_week_plan(
            plan["weekPlans"][0]["id"],
            {"title": "Week 1 logic", "focus": "Complete daily logic drills."},
        )

        self.assertEqual(updated_goal["goalName"], "2027 MEM sprint")
        self.assertEqual(updated_goal["subjects"], ["logic", "writing"])
        self.assertEqual(updated_goal["dailyAvailableMinutes"], 60)
        self.assertEqual(updated_year["title"], "MEM annual route")
        self.assertEqual(updated_month["focus"], "Stabilize logic practice.")
        self.assertEqual(updated_week["title"], "Week 1 logic")

    def test_task_update_and_completion_are_reflected(self):
        self._create_goal()
        plan = self.api.create_plan({"startDate": local_today().isoformat()})
        task_id = plan["dailyTasks"][0]["id"]

        updated = self.api.update_task(
            task_id,
            {
                "subject": "math",
                "topic": "permutation",
                "estimatedMinutes": 60,
            },
        )
        completed = self.api.complete_task(task_id)
        completed_again = self.api.complete_task(task_id)

        self.assertEqual(updated["topic"], "permutation")
        self.assertEqual(updated["estimatedMinutes"], 60)
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["completedAt"], completed_again["completedAt"])

    def test_session_start_finish_and_no_double_counting(self):
        self._create_goal()
        plan = self.api.create_plan({"startDate": local_today().isoformat()})
        task = plan["dailyTasks"][0]
        start = local_now().replace(second=0, microsecond=0)
        end = start + timedelta(minutes=35)

        session = self.api.start_session(
            {
                "taskId": task["id"],
                "startTime": start.isoformat(),
            }
        )
        finished = self.api.finish_session(
            session["id"],
            {
                "endTime": end.isoformat(),
                "notes": "finished math practice",
                "feeling": "focused",
            },
        )
        finished_again = self.api.finish_session(
            session["id"],
            {
                "endTime": (end + timedelta(minutes=40)).isoformat(),
                "notes": "should not overwrite",
            },
        )

        self.assertEqual(finished["durationMinutes"], 35)
        self.assertEqual(finished_again["durationMinutes"], 35)
        self.assertEqual(len(self.api.list_study_records()), 1)

    def test_study_home_progress_calculation(self):
        self._create_goal()
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
                "endTime": (start + timedelta(minutes=25)).isoformat(),
            },
        )

        home = self.api.get_study_home()

        self.assertEqual(home["state"], "ready")
        self.assertEqual(home["currentGoal"]["goalName"], "2027 MEM")
        self.assertEqual(home["progressSummary"]["completedTasks"], 1)
        self.assertEqual(home["progressSnapshot"]["todayStudyMinutes"], 25)
        self.assertEqual(home["progressSnapshot"]["weekStudyMinutes"], 25)

    def test_milestone_2_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("POST", "/api/study/goals"), contracts)
        self.assertIn(("GET", "/api/study/goals/active"), contracts)
        self.assertIn(("POST", "/api/study/plans"), contracts)
        self.assertIn(("PATCH", "/api/study/tasks/{task_id}/complete"), contracts)
        self.assertIn(("POST", "/api/study/sessions"), contracts)
        self.assertIn(("PATCH", "/api/study/sessions/{session_id}/finish"), contracts)


if __name__ == "__main__":
    unittest.main()
