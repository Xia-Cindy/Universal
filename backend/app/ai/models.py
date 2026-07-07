from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AIContext:
    user: dict[str, Any]
    goal: dict[str, Any] | None
    current_plan: dict[str, Any] | None
    daily_tasks: list[dict[str, Any]]
    study_sessions: list[dict[str, Any]]
    learning_events: list[dict[str, Any]]
    knowledge_sources_available: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "user": self.user,
            "goal": self.goal,
            "currentPlan": self.current_plan,
            "dailyTasks": self.daily_tasks,
            "studySessions": self.study_sessions,
            "learningEvents": self.learning_events,
            "knowledgeSourcesAvailable": self.knowledge_sources_available,
        }


@dataclass(frozen=True)
class AIRequest:
    agent_id: str
    capability: str
    user_question: str
    context: AIContext


@dataclass(frozen=True)
class AIResponse:
    answer: str
    reasoning: str
    suggested_next_action: str
    knowledge_sources_available: bool = False
    source_notice: str = "Knowledge sources are unavailable until the Knowledge/RAG milestone."

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "reasoning": self.reasoning,
            "suggestedNextAction": self.suggested_next_action,
            "knowledgeSourcesAvailable": self.knowledge_sources_available,
            "sourceNotice": self.source_notice,
        }

