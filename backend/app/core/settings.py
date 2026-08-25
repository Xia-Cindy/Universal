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
    # RAGFlow runs through amd64 emulation on the supported local macOS setup.
    # Give a cold provider enough time to return a real API error/status rather
    # than misclassifying a slow upload as an indefinite local parsing state.
    ragflow_timeout_seconds: int = int(getenv("RAGFLOW_TIMEOUT_SECONDS", "120"))
    ragflow_embedding_model: str = getenv("RAGFLOW_EMBEDDING_MODEL", "")
    ragflow_llm_model: str = getenv("RAGFLOW_LLM_MODEL", "")
    ragflow_rerank_model: str = getenv("RAGFLOW_RERANK_MODEL", "")
    # Shared AI Core provider. The API key is server-only and must never be
    # returned by an API response or stored in a user record.
    ai_provider: str = getenv("AI_PROVIDER", "deterministic")
    ai_openai_base_url: str = getenv("AI_OPENAI_BASE_URL", "")
    ai_openai_api_key: str = getenv("AI_OPENAI_API_KEY", "")
    ai_openai_model: str = getenv("AI_OPENAI_MODEL", "")
    ai_openai_timeout_seconds: int = int(getenv("AI_OPENAI_TIMEOUT_SECONDS", "45"))
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
