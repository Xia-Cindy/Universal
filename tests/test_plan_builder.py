import unittest

from backend.app.api.routes import ApiFacade


class PlanBuilderTests(unittest.TestCase):
    def test_nodes_require_parent_chain_and_tasks_can_reorder(self):
        api = ApiFacade()
        goal = api.create_goal({
            "goalType": "learning",
            "goalName": "Build systems foundations",
            "subjects": ["Operating Systems"],
            "currentLevel": "beginner",
            "dailyAvailableMinutes": 30,
            "priority": "high",
        })
        self.assertEqual(goal["goalType"], "learning")
        year = api.create_plan_node({"planType": "long_term", "title": "Systems roadmap"})
        year_id = year["yearPlan"]["id"]
        month = api.create_plan_node({"planType": "monthly", "yearPlanId": year_id, "title": "Memory month"})
        month_id = month["monthPlans"][0]["id"]
        week = api.create_plan_node({"planType": "weekly", "monthPlanId": month_id, "title": "Virtual memory week"})
        week_id = week["weekPlans"][0]["id"]
        first = api.create_plan_node({
            "planType": "daily", "weekPlanId": week_id, "title": "Task one",
            "subject": "Operating Systems", "topic": "Paging", "taskDate": "2026-07-24",
            "estimatedMinutes": 30, "sortOrder": 0,
        })
        second = api.create_plan_node({
            "planType": "daily", "weekPlanId": week_id, "title": "Task two",
            "subject": "Operating Systems", "topic": "TLB", "taskDate": "2026-07-24",
            "estimatedMinutes": 20, "sortOrder": 1,
        })
        tasks = second["dailyTasks"]
        self.assertEqual([task["topic"] for task in tasks], ["Paging", "TLB"])
        updated = api.update_task(first["dailyTasks"][0]["id"], {"sortOrder": 1})
        api.update_task(second["dailyTasks"][1]["id"], {"sortOrder": 0})
        self.assertEqual(updated["sortOrder"], 1)
        current = api.get_current_plan()
        self.assertEqual([task["topic"] for task in current["dailyTasks"]], ["TLB", "Paging"])


if __name__ == "__main__":
    unittest.main()
