from typing import Protocol


class Tool(Protocol):
    name: str

    def invoke(self, payload: dict) -> dict:
        ...


class ToolRouter(Protocol):
    def route(self, tool_name: str, payload: dict) -> dict:
        ...


class Retriever(Protocol):
    def retrieve(self, query: str, context: dict) -> list[dict]:
        ...


class DefaultToolRouter:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def route(self, tool_name: str, payload: dict) -> dict:
        tool = self._tools.get(tool_name)
        if tool is None:
            return {
                "toolName": tool_name,
                "available": False,
                "results": [],
            }
        result = tool.invoke(payload)
        return {
            "toolName": tool_name,
            "available": True,
            **result,
        }
