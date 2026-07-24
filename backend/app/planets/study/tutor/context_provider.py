from backend.app.ai import AIContext
from backend.app.services.evidence import evidence_sources


class StudyTutorContextProvider:
    """Study-specific context adapter for the Tutor capability."""

    def build(self, payload: dict) -> AIContext:
        goal = payload.get("goal") or {}
        tasks = payload.get("dailyTasks", [])
        sessions = payload.get("studySessions", [])
        learning_events = payload.get("learningEvents", [])
        memory_context = payload.get("memoryContext", {})
        memory_count = sum(len(memory_context.get(scope, [])) for scope in ("global", "planet", "session"))
        memory_context_available = memory_count > 0
        retrieval_result = payload.get("toolResults", {}).get("retrieval.search", {})
        grounding_chunks = retrieval_result.get("results", [])
        retrieval_invoked = bool(retrieval_result.get("available"))
        knowledge_sources_available = bool(grounding_chunks)
        sources = evidence_sources(grounding_chunks)
        next_task = tasks[0] if tasks else None
        goal_name = goal.get("goalName", "your active learning goal")
        task_text = (
            f" Continue with {next_task['subject']} / {next_task['topic']}."
            if next_task
            else " Create or review your next daily task."
        )
        if grounding_chunks:
            top_chunk = grounding_chunks[0]
            answer = (
                f"For {goal_name}, use the retrieved Knowledge chunk to anchor your next step: "
                f"{top_chunk['content']}{task_text}"
            )
            reasoning = (
                f"Built from Study workflow context plus {len(grounding_chunks)} retrieved "
                f"Knowledge chunk(s) and {memory_count} memory item(s). "
                f"Top match score: {top_chunk['score']}."
            )
            source_notice = "Knowledge sources are shown below. Open a source to inspect the original chunk."
        else:
            answer = (
                f"For {goal_name}, focus on the next concrete learning action."
                f"{task_text} I can use your goal, plan, daily tasks, sessions, and learning events, "
                "but no matching Knowledge chunks are available."
            )
            reasoning = (
                f"Built from Study workflow context: {len(tasks)} task(s), "
                f"{len(sessions)} finished session(s), {len(learning_events)} learning event(s), "
                f"and {memory_count} memory item(s). "
                "No Knowledge chunks were used."
            )
            source_notice = "Knowledge grounding is unavailable because no matching prepared chunks were found."
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
                "memoryContext": memory_context,
                "knowledgeSourcesAvailable": knowledge_sources_available,
                "knowledgeContext": {
                    "retrievalInvoked": retrieval_invoked,
                    "chunks": grounding_chunks,
                },
                "responseHints": {
                    "answer": answer,
                    "reasoning": reasoning,
                    "suggestedNextAction": suggested_next_action,
                    "metadata": {
                        "retrievalInvoked": retrieval_invoked,
                        "knowledgeSourcesAvailable": knowledge_sources_available,
                        "memoryContextAvailable": memory_context_available,
                        "memoryContext": memory_context,
                        "sourceNotice": source_notice,
                        "groundingChunks": grounding_chunks,
                        "sources": sources,
                    },
                },
            }
        )
