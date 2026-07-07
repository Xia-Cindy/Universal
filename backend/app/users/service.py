from dataclasses import dataclass


@dataclass(frozen=True)
class UserProfile:
    id: str
    display_name: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "displayName": self.display_name,
        }


class UserService:
    """Milestone 1 local-user boundary; auth is a later milestone."""

    def __init__(self, default_user_id: str = "local-user") -> None:
        self._default_user = UserProfile(id=default_user_id, display_name="Cindy")

    def current_user(self) -> UserProfile:
        return self._default_user

