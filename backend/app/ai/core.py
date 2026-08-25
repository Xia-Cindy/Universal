from backend.app.ai.agent_manager import AgentManager
from backend.app.ai.tools import DefaultToolRouter, ToolRouter
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
        tool_router: ToolRouter | None = None,
    ) -> None:
        self.gateway = gateway or DeterministicLLMGateway()
        self.prompt_manager = prompt_manager or PromptManager()
        self.agent_manager = agent_manager or AgentManager()
        self.context_manager = context_manager or ContextManager()
        self.tool_router = tool_router or DefaultToolRouter()

    def run(self, request: AIRequest) -> AIResponse:
        definition = self.agent_manager.resolve(
            agent_id=request.agent_id,
            capability=request.capability,
        )
        context_payload = {
            **request.context_payload,
            "toolResults": self._invoke_allowed_tools(
                allowed_tools=definition.allowed_tools,
                tool_payloads=request.tool_payloads,
            ),
        }
        context = self.context_manager.build_context(
            definition.context_builder,
            context_payload,
        )
        prompt = self.prompt_manager.get(definition.prompt_key)
        messages = [AIMessage(role="user", content=request.user_question)]
        response = self.gateway.generate(
            messages=messages,
            prompt=prompt,
            context_payload=context.to_dict(),
        )
        hints = context.to_dict().get("responseHints", {})
        hint_metadata = hints.get("metadata", {}) if isinstance(hints, dict) else {}
        return AIResponse(
            answer=response.answer,
            reasoning=response.reasoning,
            suggested_next_action=response.suggested_next_action,
            metadata={**(hint_metadata if isinstance(hint_metadata, dict) else {}), **response.metadata},
        )

    def _invoke_allowed_tools(
        self,
        *,
        allowed_tools: tuple[str, ...],
        tool_payloads: dict[str, dict],
    ) -> dict[str, dict]:
        results = {}
        for tool_name in allowed_tools:
            payload = tool_payloads.get(tool_name)
            if payload is None:
                continue
            results[tool_name] = self.tool_router.route(tool_name, payload)
        return results
