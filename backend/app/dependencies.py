"""
PRAMAAN-SHIELD — FastAPI Dependency Injection
File: backend/app/dependencies.py
"""

from fastapi import Header
from loguru import logger


async def get_api_key(x_api_key: str = Header(default=None)) -> str:
    if x_api_key is None:
        logger.warning("API call without X-API-Key header")
    return x_api_key or "anonymous"


async def get_request_language(
    accept_language: str = Header(default="hi")
) -> str:
    if "en" in accept_language.lower():
        return "en"
    return "hi"
