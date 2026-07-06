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
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"
    openrouter_fallback_model: str = (
        "qwen/qwen3-next-80b-a3b-instruct:free,google/gemma-4-31b-it:free"
    )
    llm_max_retries: int = 2
    llm_retry_backoff_seconds: float = 1.5
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1500
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    use_local_embeddings: bool = True
    jwt_secret: str = "dev_secret_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002"
    enable_live_fallback: bool = True
    agent_flow_enabled: bool = True
    declarant_pipeline_enabled: bool = True
    legacy_layperson_agent_v4: bool = False
    eurlex_research_agent_enabled: bool = True
    eurlex_research_strict_citation: bool = True
    agent_retrieval_budget_seconds: float = 55.0
    research_loop_max_iterations: int = 5
    agent_max_instruments: int = 3
    agent_max_articles_per_instrument: int = 8
    agent_max_total_chunks: int = 12
    agent_research_max_articles: int = 15
    live_fallback_timeout_seconds: float = 25.0
    retrieval_cache_ttl_seconds: int = 86400
    enable_redis_cache: bool = True
    redis_url: str = "redis://localhost:6379/0"
    fallback_score_threshold: float = 0.18
    rrf_k: int = 60
    enable_celery_ingest: bool = True
    feature_flag_live_fallback: bool = True
    feature_flag_hybrid_rrf: bool = True
    feature_flag_auto_upgrade: bool = True
    feature_flag_audit_logging: bool = True
    rerank_top_k: int = 8
    rerank_candidate_limit: int = 20
    reranker_variant: str = "control"
    eval_recall_at_5_min: float = 0.80
    eval_mrr_min: float = 0.70
    retrieval_budget_seconds: float = 8.0
    ingest_queue_max_pending: int = 200
    qdrant_hnsw_m: int = 16
    qdrant_hnsw_ef_construct: int = 100
    admin_api_key: str = ""
    jwt_auth_required: bool = False
    audit_retention_days: int = 90
    query_log_retention_days: int = 90
    feedback_retention_days: int = 365
    conversation_retention_days: int = 180
    partner_pilot_api_key: str = ""
    audit_run_token: str = ""
    layperson_conversation_llm_enabled: bool = True
    query_rate_limit: str = "20/minute"
    audit_query_rate_limit: str = "200/minute"
    internal_simulation_telemetry_enabled: bool = False


settings = Settings()
