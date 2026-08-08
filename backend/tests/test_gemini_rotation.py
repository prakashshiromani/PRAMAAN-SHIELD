"""
Unit Tests for Gemini API Key Round-Robin Rotation and 429 Failover
File: backend/tests/test_gemini_rotation.py
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from app.config import Settings
from app.services.gemini_service import GeminiService, GeminiKeySlot


def test_config_gemini_keys_parsing():
    """Verify that multiple keys separated by commas, spaces, or newlines are parsed and deduplicated."""
    settings = Settings(
        GEMINI_API_KEY="key_single_1, key_single_2",
        GEMINI_API_KEYS="key_1, key_2\nkey_3 ; key_1",
    )
    keys = settings.resolved_gemini_api_keys()
    assert keys == ["key_1", "key_2", "key_3", "key_single_1", "key_single_2"]


def test_round_robin_slot_rotation():
    """Verify that consecutive calls cycle through available slots in round-robin order."""
    service = GeminiService.__new__(GeminiService)
    service.model_name = "gemini-2.0-flash"
    service.degraded = False
    service._consecutive_failures = 0
    service._circuit_open_until = 0.0
    service._probe_active = False
    import threading
    service._lock = threading.Lock()
    service._current_slot_idx = 0

    slot1 = GeminiKeySlot(key="key_1")
    slot2 = GeminiKeySlot(key="key_2")
    slot3 = GeminiKeySlot(key="key_3")
    service._key_slots = [slot1, slot2, slot3]

    # Sequential slot selection should rotate 1 -> 2 -> 3 -> 1
    s1 = service._get_next_available_slot()
    assert s1.key == "key_1"

    s2 = service._get_next_available_slot()
    assert s2.key == "key_2"

    s3 = service._get_next_available_slot()
    assert s3.key == "key_3"

    s4 = service._get_next_available_slot()
    assert s4.key == "key_1"


def test_429_rate_limit_auto_failover():
    """Verify that when a key slot hits 429, it goes into cooldown and rotates to the next available slot."""
    service = GeminiService.__new__(GeminiService)
    service.model_name = "gemini-2.0-flash"
    service.degraded = False
    service._consecutive_failures = 0
    service._circuit_open_until = 0.0
    service._probe_active = False
    import threading
    service._lock = threading.Lock()
    service._current_slot_idx = 0

    # Mock slot 1 (will throw 429) and slot 2 (will succeed)
    mock_client1 = MagicMock()
    mock_client1.models.generate_content.side_effect = Exception("429 ResourceExhausted Quota Exceeded")

    mock_client2 = MagicMock()
    mock_response2 = MagicMock()
    mock_response2.text = '{"probability": 0.1, "perplexity": "normal", "burstiness": "normal", "reasoning": "ok", "injection_attempt": false}'
    mock_client2.models.generate_content.return_value = mock_response2

    slot1 = GeminiKeySlot(key="key_failing", client=mock_client1)
    slot2 = GeminiKeySlot(key="key_working", client=mock_client2)
    service._key_slots = [slot1, slot2]

    # Generate sync should catch 429 on slot 1, put slot 1 on cooldown, and succeed on slot 2
    res_text = service._generate_sync("test prompt")
    assert res_text == mock_response2.text
    assert slot1.cooldown_until > time.monotonic()


def test_all_keys_in_cooldown_raises():
    """Verify that when all keys are in 429 cooldown, _generate_sync raises RuntimeError."""
    service = GeminiService.__new__(GeminiService)
    service.model_name = "gemini-2.0-flash"
    service.degraded = False
    service._consecutive_failures = 0
    service._circuit_open_until = 0.0
    service._probe_active = False
    import threading
    service._lock = threading.Lock()
    service._current_slot_idx = 0

    now = time.monotonic()
    slot1 = GeminiKeySlot(key="key_1", cooldown_until=now + 60.0)
    slot2 = GeminiKeySlot(key="key_2", cooldown_until=now + 60.0)
    service._key_slots = [slot1, slot2]

    with pytest.raises(RuntimeError) as exc_info:
        service._generate_sync("test prompt")
    assert "exhausted" in str(exc_info.value).lower() or "cooldown" in str(exc_info.value).lower()
