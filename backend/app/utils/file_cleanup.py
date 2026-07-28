"""
PRAMAAN-SHIELD — 60-Second Auto-Deletion & Media Sanitation
File: backend/app/utils/file_cleanup.py
"""

import os
import asyncio
from pathlib import Path
from loguru import logger
from app.config import get_settings

settings = get_settings()


async def schedule_temp_file_deletion(file_path: str, delay_seconds: int = None):
    """
    Schedules asynchronous deletion of a temporary file after a TTL delay.
    Zero-retention requirement per TRD §1.3.
    """
    if delay_seconds is None:
        delay_seconds = settings.TEMP_FILE_TTL_SECONDS

    async def _delete():
        await asyncio.sleep(delay_seconds)
        try:
            p = Path(file_path)
            if p.exists():
                p.unlink()
                logger.info(f"Auto-deleted temp file after {delay_seconds}s: {file_path}")
        except Exception as e:
            logger.error(f"Failed to auto-delete temp file {file_path}: {e}")

    asyncio.create_task(_delete())


def ensure_upload_dir():
    """Ensure the temporary upload directory exists."""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir
