from backend.app.ai.agent_definition import AgentDefinition


class AgentManager:
    def __init__(self) -> None:
        self._definitions: dict[tuple[str, str], AgentDefinition] = {}

    def register(self, definition: AgentDefinition) -> None:
        for capability in definition.capabilities:
            self._definitions[(definition.agent_id, capability)] = definition

    def resolve(self, *, agent_id: str, capability: str) -> AgentDefinition:
        try:
            return self._definitions[(agent_id, capability)]
        except KeyError as exc:
            raise ValueError(f"Unsupported AI Core capability: {agent_id}.{capability}") from exc

