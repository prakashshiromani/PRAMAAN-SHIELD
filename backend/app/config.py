"""
PRAMAAN-SHIELD — Central Configuration
File: backend/app/config.py

Uses pydantic-settings to load, type-validate, and centralize all
environment variables. A singleton `get_settings()` function is imported
by all services.
"""

from functools import lru_cache
import secrets

from loguru import logger
from pydantic import SecretStr
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
    # Server-side pepper (secret) used to derive per-entity signing API keys.
    # Rotate this to invalidate every entity key at once. If unset, a random
    # per-boot pepper is generated so no magic default key can ever be guessed —
    # but then keys minted by a separate `seed` run will NOT match this process.
    # Set a stable ENTITY_KEY_PEPPER for multi-instance/consistent provisioning.
    ENTITY_KEY_PEPPER: SecretStr = SecretStr("")

    # Secret used to sign report download URLs (defense-in-depth until a real
    # session/auth system exists). Rotate it as part of the deployment.
    REPORT_ACCESS_SECRET: SecretStr = SecretStr("")

    # ── Scoring Weights & Thresholds ───────────────────────────────────────
    WEIGHT_SEAL_VALID: int = 45
    WEIGHT_REGISTRY_MATCH: int = 30
    WEIGHT_DOMAIN_BOUND_BONUS: int = 20      # Extra boost when every link is entity-official
    WEIGHT_ENTITY_IMPERSONATION: int = 30    # Entity named but links point elsewhere
    WEIGHT_HARD_GATE_CAP: int = 15
    WEIGHT_PHISHING_HIGH: int = 20
    WEIGHT_VOICE_SYNTHETIC: int = 40
    WEIGHT_VIDEO_DEEPFAKE: int = 25
    MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024
    UPLOAD_DIR: str = "temp_uploads"
    TEMP_FILE_TTL_SECONDS: int = 60

    # ── Hash Registry ──────────────────────────────────────────────────────
    HASH_HAMMING_THRESHOLD: int = 10

    # ── Network / Edge ─────────────────────────────────────────────────────
    # Comma-separated proxy CIDRs (e.g. "10.0.0.0/8,127.0.0.1") that are allowed
    # to set X-Forwarded-For. Empty = no proxy trust → client_ip == request.client.host.
    TRUSTED_PROXY_CIDRS: str = ""
    # Comma-separated CORS allow-list. Empty → local dev defaults.
    ALLOWED_ORIGINS: str = ""

    # ── Scan Concurrency Guard ─────────────────────────────────────────────
    MAX_CONCURRENT_SCANS: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def resolved_entity_key_pepper(self) -> str:
        """Return a usable (non-guessable) pepper for entity key derivation."""
        val = self.ENTITY_KEY_PEPPER.get_secret_value().strip()
        if val:
            return val
        # Fail-closed fallback: never a predictable constant. A random per-boot
        # pepper means this process cannot be forged, at the cost that keys from
        # an independent seed run won't match until a stable pepper is set.
        if not hasattr(self, "_generated_pepper"):
            logger.warning(
                "ENTITY_KEY_PEPPER is not set — using a random per-boot pepper. "
                "Issuer keys minted by a separate `seed` run will NOT be valid. "
                "Set ENTITY_KEY_PEPPER to a stable secret for provisioning."
            )
            self._generated_pepper = secrets.token_hex(32)
        return self._generated_pepper

    def resolved_report_access_secret(self) -> str:
        val = self.REPORT_ACCESS_SECRET.get_secret_value().strip()
        if val:
            return val
        if not hasattr(self, "_generated_report_secret"):
            logger.warning(
                "REPORT_ACCESS_SECRET is not set — using a random per-boot secret. "
                "Download tokens minted before restart will expire."
            )
            self._generated_report_secret = secrets.token_hex(32)
        return self._generated_report_secret

    def resolved_allowed_origins(self) -> list:
        """CORS allow-list. Preset in env → parse CSV. Unset → local-dev defaults."""
        if self.ALLOWED_ORIGINS.strip():
            return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://pramaan-shield.vercel.app",
        ]

    def trusted_proxy_cidrs(self) -> list:
        """Parse TRUSTED_PROXY_CIDRS into (network, netmask) pairs."""
        out = []
        for entry in self.TRUSTED_PROXY_CIDRS.split(","):
            entry = entry.strip()
            if not entry:
                continue
            try:
                import ipaddress
                network = ipaddress.ip_network(entry, strict=False)
                out.append(network)
            except ValueError:
                logger.warning(f"Ignoring invalid TRUSTED_PROXY_CIDRS entry: {entry}")
        return out


@lru_cache()
def get_settings() -> Settings:
    """
    Cached singleton settings object.
    """
    return Settings()
