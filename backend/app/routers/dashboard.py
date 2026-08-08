"""
GET /api/dashboard/stats — Dashboard Statistics Router
File: backend/app/routers/dashboard.py
"""

from fastapi import APIRouter
from app.schemas import DashboardStatsResponse
from app.services.analytics_service import get_analytics_service

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStatsResponse, tags=["dashboard"])
async def get_dashboard_stats():
    """
    Aggregate real-time system-wide statistics for the dashboard.
    Combines baseline intelligence, live in-memory test events, and persistent MongoDB counts.
    """
    from loguru import logger
    from app.db.redis import get_redis

    # Check cached stats in Redis if available
    try:
        redis = await get_redis()
        if redis is not None:
            cached = await redis.get("stats:dashboard")
            if cached:
                try:
                    import json
                    return DashboardStatsResponse.parse_raw(cached)
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"Dashboard cache read skipped: {e}")

    analytics_svc = get_analytics_service()
    response_obj = await analytics_svc.get_dashboard_stats()

    try:
        redis = await get_redis()
        if redis is not None:
            await redis.set("stats:dashboard", response_obj.json(), ex=5)
    except Exception as e:
        logger.debug(f"Dashboard cache write skipped: {e}")

    return response_obj
