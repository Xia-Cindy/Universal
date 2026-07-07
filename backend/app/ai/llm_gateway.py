from typing import Protocol

from backend.app.ai.models import AIMessage, AIResponse


class LLMGateway(Protocol):
    def generate(
        self,
        *,
        messages: list[AIMessage],
        prompt: str,
        context_payload: dict,
    ) -> AIResponse:
        ...


class DeterministicLLMGateway:
    """Provider-only deterministic gateway for local tests."""

    def generate(
        self,
        *,
        messages: list[AIMessage],
        prompt: str,
        context_payload: dict,
    ) -> AIResponse:
        hints = context_payload.get("responseHints", {})
        return AIResponse(
            answer=hints.get("answer", "Use the available context to choose the next action."),
            reasoning=hints.get("reasoning", "Generated from the provided context payload."),
            suggested_next_action=hints.get(
                "suggestedNextAction",
                "Review your current plan and continue the next task.",
            ),
            metadata=hints.get("metadata", {}),
        )

