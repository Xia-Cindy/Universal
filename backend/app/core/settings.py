from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Universe OS"
    api_prefix: str = "/api"
    default_user_id: str = "local-user"


settings = Settings()

