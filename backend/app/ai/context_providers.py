from backend.app.ai.models import AIContext


class UserContextProvider:
    def build(self, payload: dict) -> AIContext:
        return AIContext(
            {
                "user": payload.get("user", {}),
            }
        )

