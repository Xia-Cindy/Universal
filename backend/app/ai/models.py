from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AIMessage:
    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }


@dataclass(frozen=True)
class AIContext:
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return self.payload


@dataclass(frozen=True)
class AIRequest:
    agent_id: str
    capability: str
    user_question: str
    context_payload: dict[str, Any]


@dataclass(frozen=True)
class AIResponse:
    answer: str
    reasoning: str
    suggested_next_action: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "answer": self.answer,
            "reasoning": self.reasoning,
            "suggestedNextAction": self.suggested_next_action,
        }
        payload.update(self.metadata)
        return payload

