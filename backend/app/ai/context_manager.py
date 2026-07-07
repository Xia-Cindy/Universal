from typing import Protocol

from backend.app.ai.models import AIContext


class ContextProvider(Protocol):
    def build(self, payload: dict) -> AIContext:
        ...


class ContextManager:
    """Shared context orchestration for AI Core."""

    def __init__(self) -> None:
        self._providers: dict[str, ContextProvider] = {}

    def register_provider(self, key: str, provider: ContextProvider) -> None:
        self._providers[key] = provider

    def build_context(self, provider_key: str, payload: dict) -> AIContext:
        try:
            provider = self._providers[provider_key]
        except KeyError as exc:
            raise ValueError(f"Unknown context provider: {provider_key}") from exc
        return provider.build(payload)

