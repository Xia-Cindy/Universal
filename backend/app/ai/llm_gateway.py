from typing import Protocol

from backend.app.ai.models import AIRequest, AIResponse


class LLMGateway(Protocol):
    def generate(self, request: AIRequest, system_prompt: str) -> AIResponse:
        ...


class DeterministicLLMGateway:
    """Deterministic provider for local tests and provider-free development."""

    def generate(self, request: AIRequest, system_prompt: str) -> AIResponse:
        goal = request.context.goal or {}
        tasks = request.context.daily_tasks
        sessions = request.context.study_sessions
        goal_name = goal.get("goalName", "your active learning goal")
        next_task = tasks[0] if tasks else None
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
            f"{len(sessions)} finished session(s), and "
            f"{len(request.context.learning_events)} learning event(s). "
            "No RAG, embeddings, document chunks, or source citations were used."
        )
        suggested_next_action = (
            f"Start {next_task['topic']} for {next_task['estimatedMinutes']} minutes."
            if next_task
            else "Create a daily task in Plan, then record a Study Session."
        )
        return AIResponse(
            answer=answer,
            reasoning=reasoning,
            suggested_next_action=suggested_next_action,
        )

