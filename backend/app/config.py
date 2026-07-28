"""
PRAMAAN-SHIELD — Central Configuration
File: backend/app/config.py

Uses pydantic-settings to load, type-validate, and centralize all
environment variables. A singleton `get_settings()` function is imported
by all services.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Database ───────────────────────────────────────────────────────────
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "pramaan_shield"
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── AI Services ────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = "mock_gemini_key_for_dev"
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ── Telegram Bot ───────────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = "mock_telegram_token"
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = "mock_webhook_secret_32_characters_min"

    # ── DPDP Act 2023 — Privacy ────────────────────────────────────────────
    IP_HMAC_SALT: str = "default_ip_hmac_salt_32_characters_minimum_spec"

    # ── Cryptography ───────────────────────────────────────────────────────
    ENTITY_KEYS_DIR: str = "app/crypto/keys/entities"
    PRAMAAN_CA_CERT_PATH: str = "app/crypto/keys/pramaan_ca.pem"

    # ── Scoring Weights & Thresholds ───────────────────────────────────────
    SCORE_BASELINE: int = 50
    WEIGHT_KNOWN_FAKE_HASH: int = 50
    WEIGHT_SEAL_VALID: int = 45
    WEIGHT_SEAL_INVALID: int = 50
    WEIGHT_REGISTRY_MATCH: int = 15
    WEIGHT_DOMAIN_BOUND_BONUS: int = 20
    WEIGHT_ENTITY_IMPERSONATION: int = 30
    WEIGHT_HARD_GATE_CAP: int = 15
    WEIGHT_TYPOSQUAT: int = 40
    WEIGHT_PHISHING_HIGH: int = 20
    WEIGHT_VOICE_SYNTHETIC: int = 40
    MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024
    UPLOAD_DIR: str = "temp_uploads"
    TEMP_FILE_TTL_SECONDS: int = 60

    # ── Hash Registry ──────────────────────────────────────────────────────
    HASH_HAMMING_THRESHOLD: int = 10

    # ── Trust Score Internal Weights ───────────────────────────────────────
    WEIGHT_NEUTRAL_BASELINE: int = 50
    WEIGHT_HARD_GATE_CAP: int = 15
    WEIGHT_PHISHING_HIGH: int = 20
    WEIGHT_VOICE_SYNTHETIC: int = 20
    WEIGHT_VIDEO_DEEPFAKE: int = 25
    WEIGHT_SEAL_VALID: int = 45
    WEIGHT_REGISTRY_MATCH: int = 15
    WEIGHT_DOMAIN_BOUND_BONUS: int = 20      # Extra boost when every link is entity-official
    WEIGHT_ENTITY_IMPERSONATION: int = 30    # Entity named but links point elsewhere

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Cached singleton settings object.
    """
    return Settings()
