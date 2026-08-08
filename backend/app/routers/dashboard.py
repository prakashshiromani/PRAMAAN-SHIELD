"""
GET /api/dashboard/stats — Dashboard Statistics Router
File: backend/app/routers/dashboard.py
"""

from fastapi import APIRouter
from app.schemas import DashboardStatsResponse
from app.db.mongodb import get_db

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStatsResponse, tags=["dashboard"])
async def get_dashboard_stats():
    """
    Aggregate system-wide statistics for the dashboard.
    Cached in Redis for 60s so the per-request 30s polling never hammers Mongo
    with 7 count_documents + an aggregation on every browser tab.
    """
    from loguru import logger
    from app.db.redis import get_redis

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

    db = await get_db()

    total_scans = 0
    total_fakes = 0
    total_seals = 0
    reports_gen = 0
    text_count = 0
    audio_count = 0
    video_count = 0
    image_count = 0
    top_domains = []

    if db is not None:
        try:
            total_scans = await db.scan_history.count_documents({})
            total_fakes = await db.scan_history.count_documents({"verdict": "SUSPICIOUS"})
            total_seals = await db.seal_records.count_documents({"status": "active"})
            reports_gen = await db.user_reports.count_documents({})

            text_count = await db.scan_history.count_documents({"content_type": "text"})
            audio_count = await db.scan_history.count_documents({"content_type": "audio"})
            video_count = await db.scan_history.count_documents({"content_type": "video"})
            image_count = await db.scan_history.count_documents({"content_type": "image"})

            pipeline = [
                {"$match": {"verdict": "SUSPICIOUS"}},
                {"$unwind": "$checks"},
                {"$match": {"checks.module": "domain", "checks.status": "fail"}},
                {"$group": {"_id": "$checks.detail", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            cursor = db.scan_history.aggregate(pipeline)
            async for doc in cursor:
                detail = doc["_id"] or ""
                domain_part = detail.split("→")[0].strip() if "→" in detail else detail
                top_domains.append({"domain": domain_part, "count": doc["count"]})
        except Exception as e:
            logger.error(f"Failed to fetch dashboard stats from DB: {e}")

    if not top_domains:
        top_domains = [
            {"domain": "zerrodha.com", "count": 0},
            {"domain": "serbi-gov.in", "count": 0},
            {"domain": "bse-tips.in", "count": 0}
        ]

    response_obj = DashboardStatsResponse(
        total_scans=total_scans,
        total_fakes_detected=total_fakes,
        total_seals_verified=total_seals,
        reports_generated=reports_gen,
        top_flagged_domains=top_domains,
        threat_distribution={
            "text": text_count,
            "audio": audio_count,
            "video": video_count,
            "image": image_count
        }
    )

    try:
        redis = await get_redis()
        if redis is not None:
            await redis.set("stats:dashboard", response_obj.json(), ex=60)
    except Exception as e:
        logger.debug(f"Dashboard cache write skipped: {e}")

    return response_obj
