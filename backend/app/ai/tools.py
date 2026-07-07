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

