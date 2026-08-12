from collections import Counter, defaultdict

from backend.app.ai import AICoreService, AIRequest
from backend.app.knowledge.repository import KnowledgeRepository
from backend.app.models import TaskStatus
from backend.app.planets.study.repository import StudyRepository
from backend.app.planets.study.review import ReviewService
from backend.app.users.service import UserProfile


class StudyAnalyticsService:
    """Analytics module facade for Study Intelligence foundation."""

    def __init__(
        self,
        *,
        repository: StudyRepository,
        ai_core: AICoreService,
        review: ReviewService | None = None,
        knowledge_repository: KnowledgeRepository | None = None,
    ) -> None:
        self._repository = repository
        self._ai_core = ai_core
        self._review = review
        self._knowledge_repository = knowledge_repository

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

    def recommendations(self, *, user: UserProfile) -> dict[str, object]:
        """Return factual, read-only next steps; never apply a plan mutation."""

        goal = self._repository.get_active_goal(user.id)
        if not goal:
            return {
                "recommendations": [],
                "dataQuality": {
                    "state": "insufficient",
                    "limitations": ["当前还没有学习目标，无法生成目标内的学习建议。"],
                },
                "generatedFrom": {"tasks": 0, "dueReviews": 0, "readingPositions": 0},
            }

        tasks = self._repository.list_tasks_for_goal(user.id, goal.id)
        due_reviews = self._review.queue(user.id) if self._review else []
        positions = self._knowledge_repository.list_reading_progress(user.id) if self._knowledge_repository else []
        documents = {
            document.id: document
            for document in (self._knowledge_repository.list_documents(user.id) if self._knowledge_repository else [])
        }
        recommendations: list[dict[str, object]] = []

        if due_reviews:
            recommendations.append({
                "id": "complete-due-reviews",
                "kind": "review",
                "title": f"先完成 {len(due_reviews)} 个到期复习项",
                "suggestedRoute": "/study/review",
                "requiresConfirmation": True,
                "rationale": "到期复习来自已保存的错题复习队列，建议优先处理但不会自动完成。",
                "evidence": [
                    {
                        "type": "due_review",
                        "reviewId": item["review"]["id"],
                        "subject": item["wrongQuestion"].get("subject", ""),
                        "dueDate": item["review"]["dueDate"],
                    }
                    for item in due_reviews[:3]
                ],
            })

        next_task = next((task for task in tasks if task.status != TaskStatus.COMPLETED), None)
        if next_task:
            recommendations.append({
                "id": f"continue-task:{next_task.id}",
                "kind": "task",
                "title": f"继续 {next_task.subject} / {next_task.topic}",
                "suggestedRoute": "/study/plan",
                "requiresConfirmation": True,
                "rationale": "这是当前 Goal 中按既有任务顺序找到的首个未完成任务；不会自动变更状态。",
                "evidence": [{
                    "type": "incomplete_task",
                    "taskId": next_task.id,
                    "subject": next_task.subject,
                    "topic": next_task.topic,
                    "status": next_task.status.value,
                }],
            })

        for position in positions[:2]:
            document = documents.get(position.document_id)
            if not document:
                continue
            recommendations.append({
                "id": f"resume-reading:{document.id}",
                "kind": "reading",
                "title": f"继续阅读《{document.file_name}》第 {position.page_number} 页",
                "suggestedRoute": "/study/knowledge",
                "requiresConfirmation": True,
                "rationale": "这是你主动保存的阅读位置；打开资料后仍可自行选择其它页面。",
                "evidence": [{
                    "type": "reading_progress",
                    "documentId": document.id,
                    "pageNumber": position.page_number,
                    "spreadIndex": position.spread_index,
                    "updatedAt": position.updated_at.isoformat(),
                }],
            })

        return {
            "recommendations": recommendations,
            "dataQuality": {
                "state": "ready" if recommendations else "insufficient",
                "limitations": [] if recommendations else ["当前 Goal 没有未完成任务、到期复习或已同步的阅读位置。"],
            },
            "generatedFrom": {
                "tasks": len(tasks),
                "dueReviews": len(due_reviews),
                "readingPositions": len(positions),
            },
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
            "review": self._review.summary(user.id) if self._review else {
                "wrongQuestionCount": 0,
                "reviewQueueCount": 0,
                "dueReviewCount": 0,
                "completedReviewCount": 0,
            },
        }
        data_quality = self._data_quality(tasks=tasks, sessions=sessions)
        learning_insights = self._learning_insights(progress, weak_areas, memory_context)
        recommended_actions = self._recommended_actions(tasks, weak_areas)
        if progress["review"]["dueReviewCount"]:
            recommended_actions.insert(0, f"完成 {progress['review']['dueReviewCount']} 个到期复习项。")
        report_summary = (
            "学习数据已经足够生成基础分析。"
            if data_quality["state"] == "ready"
            else "学习数据还不够，请先完成更多任务和学习记录。"
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
            "recommendedActions": ["先创建一个学习目标，并为它建立学习计划。"],
            "report": {
                "summary": "需要先有当前学习目标，Analytics 才能解释学习进展。",
                "mode": "empty",
                "actionsApplied": [],
            },
            "dataQuality": {
                "state": "insufficient",
                "limitations": ["当前还没有学习目标。"],
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
            limitations.append("当前目标还没有每日任务。")
        if not sessions:
            limitations.append("还没有完成的学习记录。")
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
            f"当前任务完成率为 {int(progress['taskCompletionRate'] * 100)}%。",
            f"累计已记录学习时间 {progress['totalStudyMinutes']} 分钟。",
        ]
        if weak_areas:
            insights.append(f"{len(weak_areas)} 个主题推进偏慢，需要更稳定的学习节奏。")
        memory_count = sum(len(memory_context.get(scope, [])) for scope in ("global", "planet", "session"))
        if memory_count:
            insights.append(f"已有 {memory_count} 条 Memory 可用于理解你的学习状态。")
        return insights

    def _recommended_actions(self, tasks, weak_areas: list[dict[str, object]]) -> list[str]:
        next_task = next((task for task in tasks if task.status != TaskStatus.COMPLETED), None)
        actions = []
        if next_task:
            actions.append(f"继续完成 {next_task.subject} / {next_task.topic}。")
        if weak_areas:
            actions.append(f"为 {weak_areas[0]['subject']} 安排一次专注学习。")
        if not actions:
            actions.append("回顾已完成任务，并规划下一周学习。")
        return actions

    def _retrieval_query(self, payload: dict[str, object]) -> str:
        weak_areas = payload.get("weakAreas", [])
        if weak_areas:
            return f"Study analytics weak area {weak_areas[0]['subject']}"
        goal = payload["progressSummary"].get("goal")
        if goal:
            return f"Study analytics for {goal['goalName']}"
        return "Study analytics"
