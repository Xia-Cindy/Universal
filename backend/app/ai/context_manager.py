from typing import Any

from backend.app.ai.models import AIContext


class ContextManager:
    """Shared AI Core context normalizer.

    Milestone 3 intentionally accepts only workflow context and marks
    knowledge sources unavailable.
    """

    def build_study_context(
        self,
        *,
        user: dict[str, Any],
        goal: dict[str, Any] | None,
        current_plan: dict[str, Any] | None,
        daily_tasks: list[dict[str, Any]],
        study_sessions: list[dict[str, Any]],
        learning_events: list[dict[str, Any]],
    ) -> AIContext:
        return AIContext(
            user=user,
            goal=goal,
            current_plan=current_plan,
            daily_tasks=daily_tasks,
            study_sessions=study_sessions,
            learning_events=learning_events,
            knowledge_sources_available=False,
        )

