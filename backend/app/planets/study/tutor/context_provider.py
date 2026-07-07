from backend.app.ai import AIContext


class StudyTutorContextProvider:
    """Study-specific context adapter for the Tutor capability."""

    def build(self, payload: dict) -> AIContext:
        goal = payload.get("goal") or {}
        tasks = payload.get("dailyTasks", [])
        sessions = payload.get("studySessions", [])
        learning_events = payload.get("learningEvents", [])
        next_task = tasks[0] if tasks else None
        goal_name = goal.get("goalName", "your active learning goal")
        task_text = (
            f" Continue with {next_task['subject']} / {next_task['topic']}."
            if next_task
            else " Create or review your next daily task."
        )
        answer = (
            f"For {goal_name}, focus on the next concrete learning action."
            f"{task_text} I can use your goal, plan, daily tasks, sessions, and learning events, "
            "but uploaded knowledge sources are not available yet."
        )
        reasoning = (
            f"Built from Study workflow context: {len(tasks)} task(s), "
            f"{len(sessions)} finished session(s), and {len(learning_events)} learning event(s). "
            "No RAG, embeddings, document chunks, or source citations were used."
        )
        suggested_next_action = (
            f"Start {next_task['topic']} for {next_task['estimatedMinutes']} minutes."
            if next_task
            else "Create a daily task in Plan, then record a Study Session."
        )
        return AIContext(
            {
                "user": payload.get("user", {}),
                "goal": goal or None,
                "currentPlan": payload.get("currentPlan"),
                "dailyTasks": tasks,
                "studySessions": sessions,
                "learningEvents": learning_events,
                "knowledgeSourcesAvailable": False,
                "responseHints": {
                    "answer": answer,
                    "reasoning": reasoning,
                    "suggestedNextAction": suggested_next_action,
                    "metadata": {
                        "knowledgeSourcesAvailable": False,
                        "sourceNotice": "Knowledge sources are unavailable until the Knowledge/RAG milestone.",
                    },
                },
            }
        )

