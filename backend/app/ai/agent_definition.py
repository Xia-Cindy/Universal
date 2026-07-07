from dataclasses import dataclass


@dataclass(frozen=True)
class AgentDefinition:
    agent_id: str
    capabilities: tuple[str, ...]
    prompt_key: str
    context_builder: str
    allowed_tools: tuple[str, ...] = ()

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities

