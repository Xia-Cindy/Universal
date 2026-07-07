class AgentManager:
    def resolve(self, *, agent_id: str, capability: str) -> dict[str, str]:
        if agent_id == "study" and capability == "tutor":
            return {
                "agentId": "study",
                "agentName": "Study Agent",
                "capability": "tutor",
            }
        raise ValueError(f"Unsupported AI Core capability: {agent_id}.{capability}")

