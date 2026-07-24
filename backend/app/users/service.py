from dataclasses import dataclass

from backend.app.persistence.sqlite import SQLitePersistence


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

    def __init__(self, default_user_id: str = "local-user", persistence: SQLitePersistence | None = None) -> None:
        self._default_user = UserProfile(id=default_user_id, display_name="Cindy")
        self._persistence = persistence
        if persistence:
            with persistence.transaction() as db:
                db.execute(
                    "INSERT INTO users(id,display_name,created_at) VALUES(?,?,datetime('now')) ON CONFLICT(id) DO NOTHING",
                    (default_user_id, self._default_user.display_name),
                )

    def current_user(self) -> UserProfile:
        return self._default_user
