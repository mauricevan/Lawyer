"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central config — no secrets in code."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://lawyer:lawyer_dev@localhost:5432/lawyer"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "eurlex_chunks"
    llm_provider: str = "openrouter"
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemma-4-31b-it:free"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    use_local_embeddings: bool = True
    jwt_secret: str = "dev_secret_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"


settings = Settings()
