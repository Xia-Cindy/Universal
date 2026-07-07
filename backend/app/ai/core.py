from backend.app.ai.agent_manager import AgentManager
from backend.app.ai.llm_gateway import DeterministicLLMGateway, LLMGateway
from backend.app.ai.models import AIMessage, AIRequest, AIResponse
from backend.app.ai.prompt_manager import PromptManager
from backend.app.ai.context_manager import ContextManager


class AICoreService:
    """Shared AI Core service entry point."""

    def __init__(
        self,
        *,
        gateway: LLMGateway | None = None,
        prompt_manager: PromptManager | None = None,
        agent_manager: AgentManager | None = None,
        context_manager: ContextManager | None = None,
    ) -> None:
        self.gateway = gateway or DeterministicLLMGateway()
        self.prompt_manager = prompt_manager or PromptManager()
        self.agent_manager = agent_manager or AgentManager()
        self.context_manager = context_manager or ContextManager()

    def run(self, request: AIRequest) -> AIResponse:
        definition = self.agent_manager.resolve(
            agent_id=request.agent_id,
            capability=request.capability,
        )
        context = self.context_manager.build_context(
            definition.context_builder,
            request.context_payload,
        )
        prompt = self.prompt_manager.get(definition.prompt_key)
        messages = [AIMessage(role="user", content=request.user_question)]
        return self.gateway.generate(
            messages=messages,
            prompt=prompt,
            context_payload=context.to_dict(),
        )

