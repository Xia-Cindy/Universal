from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    app_name: str = "Universe OS"
    api_prefix: str = "/api"
    default_user_id: str = "local-user"
    knowledge_provider: str = getenv("KNOWLEDGE_PROVIDER", "local")
    ragflow_base_url: str = getenv("RAGFLOW_BASE_URL", "http://127.0.0.1:9380")
    ragflow_api_key: str = getenv("RAGFLOW_API_KEY", "")
    ragflow_dataset_id: str = getenv("RAGFLOW_DATASET_ID", "")
    ragflow_dataset_name: str = getenv("RAGFLOW_DATASET_NAME", "Universe OS Knowledge")


settings = Settings()
