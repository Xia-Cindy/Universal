from backend.app.ai.agent_manager import AgentManager
from backend.app.ai.llm_gateway import DeterministicLLMGateway, LLMGateway
from backend.app.ai.models import AIRequest, AIResponse
from backend.app.ai.prompt_manager import PromptManager


class AICoreService:
    """Shared AI Core service entry point."""

    def __init__(
        self,
        *,
        gateway: LLMGateway | None = None,
        prompt_manager: PromptManager | None = None,
        agent_manager: AgentManager | None = None,
    ) -> None:
        self._gateway = gateway or DeterministicLLMGateway()
        self._prompt_manager = prompt_manager or PromptManager()
        self._agent_manager = agent_manager or AgentManager()

    def run(self, request: AIRequest) -> AIResponse:
        self._agent_manager.resolve(agent_id=request.agent_id, capability=request.capability)
        prompt = self._prompt_manager.system_prompt(
            agent_id=request.agent_id,
            capability=request.capability,
        )
        return self._gateway.generate(request, prompt)

