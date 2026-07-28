"""
PRAMAAN-SHIELD — Loguru Logger Configuration
File: backend/app/utils/logger.py
"""

import sys
from loguru import logger


def configure_logger(log_level: str = "DEBUG", log_dir: str = "logs") -> None:
    """Configure all logger sinks."""
    logger.remove()

    logger.add(
        sys.stdout,
        level=log_level,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    )

    logger.add(
        f"{log_dir}/pramaan_{{time:YYYY-MM-DD}}.log",
        level="INFO",
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        format="{time} | {level} | {module}:{function}:{line} | {message}"
    )

    logger.add(
        f"{log_dir}/structured.jsonl",
        level="INFO",
        serialize=True,
        rotation="50 MB",
        retention="30 days"
    )

    logger.info("Logger initialized — PRAMAAN-SHIELD backend starting")
