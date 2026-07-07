class PromptManager:
    def system_prompt(self, *, agent_id: str, capability: str) -> str:
        if agent_id == "study" and capability == "tutor":
            return (
                "You are the Study Agent Tutor capability. Use only Study workflow context: "
                "user profile, active goal, current plan, daily tasks, study sessions, and learning events. "
                "Do not cite uploaded material, documents, RAG, embeddings, or Knowledge Graph data."
            )
        return "You are an AI Core capability. Use only the provided context."

