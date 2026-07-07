class PromptManager:
    def __init__(self) -> None:
        self._prompts: dict[str, str] = {}

    def register(self, key: str, prompt: str) -> None:
        self._prompts[key] = prompt

    def get(self, key: str) -> str:
        try:
            return self._prompts[key]
        except KeyError as exc:
            raise ValueError(f"Unknown prompt key: {key}") from exc

