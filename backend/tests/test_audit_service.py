"""
Test Immutable Audit Ledger Service
File: backend/tests/test_audit_service.py
"""

import pytest
from app.services.audit_service import log_audit, ALLOWED_ACTIONS


def test_allowed_actions_set():
    assert "SIGN_SEAL" in ALLOWED_ACTIONS
    assert "REVOKE_SEAL" in ALLOWED_ACTIONS
    assert "REGISTRY_ADD" in ALLOWED_ACTIONS


@pytest.mark.asyncio
async def test_invalid_action_raises_value_error():
    with pytest.raises(ValueError, match="Invalid audit action"):
        await log_audit(
            action="INVALID_ACTION_TYPE",
            actor_entity="TEST",
            actor_reg_no="123",
            resource_id="res_1",
            metadata={}
        )
