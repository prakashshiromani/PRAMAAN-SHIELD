"""
Pytest Shared Fixtures
File: backend/tests/conftest.py
"""

import asyncio
import os
import pytest
from unittest.mock import AsyncMock, MagicMock

# Environment overrides for test execution
os.environ["IP_HMAC_SALT"] = "test_salt_32_characters_minimum_spec_salt!"
os.environ["GEMINI_API_KEY"] = "mock_test_key"
os.environ["TELEGRAM_BOT_TOKEN"] = "mock_test_token"
os.environ["TELEGRAM_WEBHOOK_SECRET"] = "mock_test_secret_32_characters_minimum"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.sebi_registry.find_one = AsyncMock(return_value=None)
    db.seal_records.find_one = AsyncMock(return_value=None)
    db.audit_ledger.insert_one = AsyncMock(return_value=True)
    return db
