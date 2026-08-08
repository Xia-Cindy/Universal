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
    ragflow_embedding_model: str = getenv("RAGFLOW_EMBEDDING_MODEL", "")
    ragflow_llm_model: str = getenv("RAGFLOW_LLM_MODEL", "")
    ragflow_rerank_model: str = getenv("RAGFLOW_RERANK_MODEL", "")
    # PostgreSQL is the Universe runtime data store. SQLite remains available
    # only when a local developer explicitly opts into it.
    persistence_backend: str = getenv("PERSISTENCE_BACKEND", "postgres")
    database_path: str = getenv("UNIVERSE_DATABASE_PATH", "database/universe.sqlite3")
    database_url: str = getenv("DATABASE_URL", "")
    object_storage_backend: str = getenv("OBJECT_STORAGE_BACKEND", "local")
    object_storage_root: str = getenv("OBJECT_STORAGE_ROOT", "storage/objects")
    object_storage_bucket: str = getenv("OBJECT_STORAGE_BUCKET", "")
    object_storage_region: str = getenv("OBJECT_STORAGE_REGION", "us-east-1")
    object_storage_endpoint_url: str = getenv("OBJECT_STORAGE_ENDPOINT_URL", "")
    object_storage_access_key_id: str = getenv("OBJECT_STORAGE_ACCESS_KEY_ID", "")
    object_storage_secret_access_key: str = getenv("OBJECT_STORAGE_SECRET_ACCESS_KEY", "")
    email_backend: str = getenv("EMAIL_BACKEND", "console")
    smtp_host: str = getenv("SMTP_HOST", "")
    smtp_port: int = int(getenv("SMTP_PORT", "465"))
    smtp_username: str = getenv("SMTP_USERNAME", "")
    smtp_password: str = getenv("SMTP_PASSWORD", "")
    smtp_from: str = getenv("SMTP_FROM", "")


settings = Settings()
