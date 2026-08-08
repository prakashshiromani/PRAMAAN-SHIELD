"""
PRAMAAN-SHIELD — FastAPI Dependency Injection
File: backend/app/dependencies.py
"""

from fastapi import Header
from loguru import logger


from fastapi import HTTPException, status
from app.db.mongodb import get_db
from app.crypto.seal_engine import api_key_hash


async def get_authenticated_entity(x_api_key: str = Header(default=None)) -> dict:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header"
        )

    db = await get_db()
    entity = None
    if db is not None:
        try:
            entity = await db.sebi_registry.find_one({
                "api_key_hash": api_key_hash(x_api_key)
            })
        except Exception as e:
            logger.warning(f"DB entity key lookup failed: {e}")
            entity = None

    if entity and entity.get("key_status") == "active":
        return {
            "entity_name": entity["entity_name"],
            "registration_number": entity["registration_number"]
        }

    # Fail-closed: an unknown or inactive key must never mint a seal. The old
    # guessable 'key_REGULATOR_2026' magic key was removed (Issue #02).
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or inactive X-API-Key"
    )
