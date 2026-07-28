"""
Test Settings & Configuration
File: backend/tests/test_config.py
"""

from app.config import get_settings


def test_settings_load():
    settings = get_settings()
    assert settings.DB_NAME == "pramaan_shield"
    assert settings.MAX_UPLOAD_BYTES == 52428800
    assert len(settings.IP_HMAC_SALT) >= 32
