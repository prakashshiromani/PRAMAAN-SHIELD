"""
PRAMAAN-SHIELD — Immutable Audit Ledger Service
File: backend/app/services/audit_service.py

Records every trust-changing action for regulatory traceability.
Backend SCHEMA.md §1.6 defines the audit_ledger collection schema.

Supported action enums:
  SIGN_SEAL       → Entity signs a new PRAMAAN Seal
  REVOKE_SEAL     → Entity revokes an existing seal
  FLAG_CONTENT    → Verified entity flags content as fake
  REGISTRY_ADD    → New entity added to SEBI registry
  REGISTRY_UPDATE → Entity registry record modified
  KEY_ROTATE      → Entity public key is rotated
  KEY_REVOKE      → Entity public key is revoked
"""

import uuid
from datetime import datetime, timezone
from loguru import logger
from app.db.mongodb import get_db
from app.utils.privacy import pseudonymize_ip

ALLOWED_ACTIONS = {
    "SIGN_SEAL", "REVOKE_SEAL", "FLAG_CONTENT",
    "REGISTRY_ADD", "REGISTRY_UPDATE", "KEY_ROTATE", "KEY_REVOKE"
}


async def log_audit(
    action: str,
    actor_entity: str,
    actor_reg_no: str,
    resource_id: str,
    metadata: dict,
    ip_address: str = "0.0.0.0"
) -> str:
    """
    Write an immutable audit entry to audit_ledger.

    Args:
        action:       One of ALLOWED_ACTIONS enum
        actor_entity: Entity name e.g. "SEBI"
        actor_reg_no: SEBI registration number e.g. "REGULATOR"
        resource_id:  What was acted on (seal_id, entity_name, etc.)
        metadata:     Dict of additional context
        ip_address:   Raw IP — will be HMAC-pseudonymized before storage

    Returns:
        audit_id: The unique audit record ID
    """
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Invalid audit action: {action}. Must be one of {ALLOWED_ACTIONS}")

    audit_id = f"aud_{uuid.uuid4().hex}"
    ip_hmac = pseudonymize_ip(ip_address)

    record = {
        "audit_id": audit_id,
        "action": action,
        "actor_entity": actor_entity,
        "actor_registration_number": actor_reg_no,
        "resource_id": resource_id,
        "metadata": metadata,
        "ip_hmac": ip_hmac,
        "timestamp": datetime.now(timezone.utc)
    }

    db = await get_db()
    if db is None:
        logger.warning("Audit log skipped (MongoDB offline)")
        return "aud_unpersisted"
    await db.audit_ledger.insert_one(record)
    logger.info(f"Audit logged: {action} by {actor_entity} on {resource_id}")
    return audit_id
