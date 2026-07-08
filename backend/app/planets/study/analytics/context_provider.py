from backend.app.ai import AIContext


class StudyAnalystContextProvider:
    """Study-specific context adapter for the Analyst capability."""

    def build(self, payload: dict) -> AIContext:
        metrics = payload.get("metrics", {})
        data_quality = payload.get("dataQuality", {})
        memory_context = payload.get("memoryContext", {})
        retrieval_result = payload.get("toolResults", {}).get("retrieval.search", {})
        grounding_chunks = retrieval_result.get("results", [])
        retrieval_invoked = bool(retrieval_result.get("available"))
        memory_count = sum(len(memory_context.get(scope, [])) for scope in ("global", "planet", "session"))
        completed = metrics.get("completedTasks", 0)
        total = metrics.get("totalTasks", 0)
        minutes = metrics.get("totalStudyMinutes", 0)
        weak_areas = payload.get("weakAreas", [])

        if data_quality.get("state") == "insufficient":
            insights = [
                "Create a learning Goal and complete Study Sessions before relying on trend analysis."
            ]
            actions = ["Create a Goal, generate a Plan, and finish at least one Study Session."]
            report = (
                "There is not enough Study data yet. Analytics can explain progress after Goals, "
                "Daily Tasks, and Study Sessions exist."
            )
        else:
            insights = [
                f"{completed} of {total} tasks are completed.",
                f"Recorded study time is {minutes} minutes.",
            ]
            if memory_count:
                insights.append(f"{memory_count} prepared memory item(s) can inform interpretation.")
            if grounding_chunks:
                insights.append(f"{len(grounding_chunks)} Knowledge chunk(s) were available for grounding.")
            actions = payload.get("recommendedActions", [])
            report = (
                "Your Study pattern is becoming measurable. Continue with the next incomplete task, "
                "then use Study Sessions to keep progress signals fresh."
            )

        return AIContext(
            {
                "metrics": metrics,
                "memoryContext": memory_context,
                "knowledgeContext": {
                    "retrievalInvoked": retrieval_invoked,
                    "chunks": grounding_chunks,
                },
                "responseHints": {
                    "answer": report,
                    "reasoning": (
                        f"Analyst used Study metrics, {memory_count} memory item(s), "
                        f"and {len(grounding_chunks)} Knowledge chunk(s)."
                    ),
                    "suggestedNextAction": actions[0] if actions else "Continue the next Study task.",
                    "metadata": {
                        "progressSummary": metrics,
                        "learningInsights": insights,
                        "weakAreas": weak_areas,
                        "recommendedActions": actions,
                        "report": {
                            "summary": report,
                            "retrievalInvoked": retrieval_invoked,
                            "groundingChunks": grounding_chunks,
                            "actionsApplied": [],
                        },
                        "dataQuality": data_quality,
                        "actionsApplied": [],
                    },
                },
            }
        )
