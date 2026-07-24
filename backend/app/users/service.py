from dataclasses import dataclass
from contextvars import ContextVar

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
        self._current_user: ContextVar[UserProfile] = ContextVar("universe_current_user", default=self._default_user)
        self._profiles = {self._default_user.id: self._default_user}
        self._persistence = persistence
        if persistence:
            with persistence.transaction() as db:
                db.execute(
                    "INSERT INTO users(id,display_name,created_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(id) DO NOTHING",
                    (default_user_id, self._default_user.display_name),
                )

    def current_user(self) -> UserProfile:
        return self._current_user.get()

    def set_current_user(self, user: UserProfile):
        return self._current_user.set(user)

    def reset_current_user(self, token) -> None:
        self._current_user.reset(token)

    def create_user(self, user_id: str, display_name: str) -> UserProfile:
        profile = UserProfile(id=user_id, display_name=display_name)
        self._profiles[profile.id] = profile
        if self._persistence:
            with self._persistence.transaction() as db:
                db.execute(
                    "INSERT INTO users(id,display_name,created_at) VALUES(?,?,CURRENT_TIMESTAMP)",
                    (profile.id, profile.display_name),
                )
        return profile

    def get_user(self, user_id: str) -> UserProfile:
        if user_id in self._profiles:
            return self._profiles[user_id]
        if self._persistence:
            row = self._persistence.connection.execute(
                "SELECT id, display_name FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if row:
                profile = UserProfile(id=row["id"], display_name=row["display_name"])
                self._profiles[profile.id] = profile
                return profile
        raise KeyError(user_id)
