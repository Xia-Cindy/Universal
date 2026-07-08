from collections import Counter, defaultdict

from backend.app.ai import AICoreService, AIRequest
from backend.app.models import TaskStatus
from backend.app.planets.study.repository import StudyRepository
from backend.app.users.service import UserProfile


class StudyAnalyticsService:
    """Analytics module facade for Study Intelligence foundation."""

    def __init__(self, *, repository: StudyRepository, ai_core: AICoreService) -> None:
        self._repository = repository
        self._ai_core = ai_core

    def analytics(
        self,
        *,
        user: UserProfile,
        memory_context: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return self._build_payload(user=user, memory_context=memory_context or {}, use_ai=False)

    def report(
        self,
        *,
        user: UserProfile,
        memory_context: dict[str, object] | None = None,
    ) -> dict[str, object]:
        payload = self._build_payload(user=user, memory_context=memory_context or {}, use_ai=True)
        ai_response = self._ai_core.run(
            AIRequest(
                agent_id="study",
                capability="analyst",
                user_question="Generate Study Analytics report",
                context_payload={
                    "metrics": payload["progressSummary"],
                    "dataQuality": payload["dataQuality"],
                    "weakAreas": payload["weakAreas"],
                    "recommendedActions": payload["recommendedActions"],
                    "memoryContext": memory_context or {},
                },
                tool_payloads={
                    "retrieval.search": {
                        "userId": user.id,
                        "query": self._retrieval_query(payload),
                        "limit": 3,
                    }
                },
            )
        )
        response = ai_response.to_dict()
        return {
            "progressSummary": response.get("progressSummary", payload["progressSummary"]),
            "learningInsights": response.get("learningInsights", payload["learningInsights"]),
            "weakAreas": response.get("weakAreas", payload["weakAreas"]),
            "recommendedActions": response.get("recommendedActions", payload["recommendedActions"]),
            "report": response.get("report", payload["report"]),
            "dataQuality": response.get("dataQuality", payload["dataQuality"]),
        }

    def _build_payload(
        self,
        *,
        user: UserProfile,
        memory_context: dict[str, object],
        use_ai: bool,
    ) -> dict[str, object]:
        goal = self._repository.get_active_goal(user.id)
        if not goal:
            return self._empty_payload()

        tasks = self._repository.list_tasks_for_goal(user.id, goal.id)
        sessions = self._repository.list_finished_sessions(user.id)
        learning_events = self._repository.list_learning_events(user.id)
        completed_tasks = [task for task in tasks if task.status == TaskStatus.COMPLETED]
        subject_minutes: dict[str, int] = defaultdict(int)
        for session in sessions:
            subject_minutes[session.subject] += session.duration_minutes
        subject_completion = self._subject_completion(tasks)
        weak_areas = self._weak_areas(subject_completion, subject_minutes)
        total_minutes = sum(session.duration_minutes for session in sessions)
        progress = {
            "goal": goal.to_dict(),
            "totalTasks": len(tasks),
            "completedTasks": len(completed_tasks),
            "taskCompletionRate": round(len(completed_tasks) / len(tasks), 2) if tasks else 0,
            "totalStudyMinutes": total_minutes,
            "finishedSessions": len(sessions),
            "learningEvents": len(learning_events),
            "subjectMinutes": dict(sorted(subject_minutes.items())),
            "subjectCompletion": subject_completion,
        }
        data_quality = self._data_quality(tasks=tasks, sessions=sessions)
        learning_insights = self._learning_insights(progress, weak_areas, memory_context)
        recommended_actions = self._recommended_actions(tasks, weak_areas)
        report_summary = (
            "Study data is ready for interpretation."
            if data_quality["state"] == "ready"
            else "Study data is still limited; complete more tasks and sessions."
        )
        return {
            "progressSummary": progress,
            "learningInsights": learning_insights,
            "weakAreas": weak_areas,
            "recommendedActions": recommended_actions,
            "report": {
                "summary": report_summary,
                "mode": "ai" if use_ai else "metrics",
                "actionsApplied": [],
            },
            "dataQuality": data_quality,
        }

    def _empty_payload(self) -> dict[str, object]:
        return {
            "progressSummary": {
                "goal": None,
                "totalTasks": 0,
                "completedTasks": 0,
                "taskCompletionRate": 0,
                "totalStudyMinutes": 0,
                "finishedSessions": 0,
                "learningEvents": 0,
                "subjectMinutes": {},
                "subjectCompletion": {},
            },
            "learningInsights": [],
            "weakAreas": [],
            "recommendedActions": ["Create a Goal and generate a Study Plan."],
            "report": {
                "summary": "Analytics needs an active Goal before it can explain progress.",
                "mode": "empty",
                "actionsApplied": [],
            },
            "dataQuality": {
                "state": "insufficient",
                "limitations": ["No active Goal exists."],
            },
        }

    def _subject_completion(self, tasks) -> dict[str, dict[str, int]]:
        totals = Counter(task.subject for task in tasks)
        completed = Counter(task.subject for task in tasks if task.status == TaskStatus.COMPLETED)
        return {
            subject: {
                "totalTasks": totals[subject],
                "completedTasks": completed[subject],
            }
            for subject in sorted(totals)
        }

    def _weak_areas(
        self,
        subject_completion: dict[str, dict[str, int]],
        subject_minutes: dict[str, int],
    ) -> list[dict[str, object]]:
        areas = []
        for subject, completion in subject_completion.items():
            total = completion["totalTasks"]
            completed = completion["completedTasks"]
            completion_rate = round(completed / total, 2) if total else 0
            if completion_rate < 0.5:
                areas.append(
                    {
                        "subject": subject,
                        "reason": "low_task_completion",
                        "completionRate": completion_rate,
                        "studyMinutes": subject_minutes.get(subject, 0),
                    }
                )
        return areas

    def _data_quality(self, *, tasks, sessions) -> dict[str, object]:
        limitations = []
        if not tasks:
            limitations.append("No Daily Tasks exist.")
        if not sessions:
            limitations.append("No finished Study Sessions exist.")
        return {
            "state": "ready" if not limitations else "insufficient",
            "limitations": limitations,
        }

    def _learning_insights(
        self,
        progress: dict[str, object],
        weak_areas: list[dict[str, object]],
        memory_context: dict[str, object],
    ) -> list[str]:
        insights = [
            f"Task completion is {progress['taskCompletionRate']}.",
            f"Finished study time is {progress['totalStudyMinutes']} minutes.",
        ]
        if weak_areas:
            insights.append(f"{len(weak_areas)} subject(s) need steadier follow-through.")
        memory_count = sum(len(memory_context.get(scope, [])) for scope in ("global", "planet", "session"))
        if memory_count:
            insights.append(f"{memory_count} memory item(s) are available for interpretation.")
        return insights

    def _recommended_actions(self, tasks, weak_areas: list[dict[str, object]]) -> list[str]:
        next_task = next((task for task in tasks if task.status != TaskStatus.COMPLETED), None)
        actions = []
        if next_task:
            actions.append(f"Continue {next_task.subject} / {next_task.topic}.")
        if weak_areas:
            actions.append(f"Schedule a focused session for {weak_areas[0]['subject']}.")
        if not actions:
            actions.append("Review your completed tasks and plan the next week.")
        return actions

    def _retrieval_query(self, payload: dict[str, object]) -> str:
        weak_areas = payload.get("weakAreas", [])
        if weak_areas:
            return f"Study analytics weak area {weak_areas[0]['subject']}"
        goal = payload["progressSummary"].get("goal")
        if goal:
            return f"Study analytics for {goal['goalName']}"
        return "Study analytics"
