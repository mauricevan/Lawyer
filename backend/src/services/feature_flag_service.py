"""Runtime feature flags loaded from environment settings."""
from backend.src.config import settings


class FeatureFlagService:
    """Checks whether optional product features are enabled."""

    def is_live_fallback_enabled(self) -> bool:
        return settings.enable_live_fallback and settings.feature_flag_live_fallback

    def is_hybrid_rrf_enabled(self) -> bool:
        return settings.feature_flag_hybrid_rrf

    def is_auto_upgrade_enabled(self) -> bool:
        return settings.feature_flag_auto_upgrade

    def is_audit_logging_enabled(self) -> bool:
        return settings.feature_flag_audit_logging
