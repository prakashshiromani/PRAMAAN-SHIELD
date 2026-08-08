"""
PRAMAAN-SHIELD — Centralized Analytics & Real-Time Metrics Service
File: backend/app/services/analytics_service.py

Responsibilities:
1. 100% real live tracking of security scans, deepfakes, phishing domains, seal verifications, and redressal reports.
2. Real-time in-memory session tracking + persistent MongoDB aggregations (no hardcoded/fake numbers).
3. Instant cache invalidation on new detection events.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from collections import Counter
import asyncio
import re
from loguru import logger
from app.schemas import DashboardStatsResponse
from app.db.mongodb import get_db


class AnalyticsService:
    _instance: Optional["AnalyticsService"] = None

    def __new__(cls) -> "AnalyticsService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self._live_scans: int = 0
        self._live_fakes: int = 0
        self._live_seals_verified: int = 0
        self._live_seals_issued: int = 0
        self._live_reports_generated: int = 0

        self._live_media_counts: Dict[str, int] = {
            "text": 0,
            "audio": 0,
            "video": 0,
            "image": 0
        }

        # Real-time dynamic domain detection counter (starts completely clean)
        self._live_domain_counts: Counter = Counter()

    def record_scan(
        self,
        content_type: str,
        verdict: str,
        checks: Optional[List[Dict[str, Any]]] = None,
        flagged_domain: Optional[str] = None
    ):
        """Record a real scan execution into real-time metrics."""
        self._live_scans += 1

        ct = str(content_type).lower()
        if ct in self._live_media_counts:
            self._live_media_counts[ct] += 1
        else:
            self._live_media_counts["text"] += 1

        verdict_str = str(verdict).upper()
        if verdict_str in ["SUSPICIOUS", "FAIL"]:
            self._live_fakes += 1

        # Extract flagged domains from explicit parameter
        if flagged_domain:
            clean_d = self._sanitize_domain(flagged_domain)
            if clean_d:
                self._live_domain_counts[clean_d] += 1

        # Extract flagged domains from security checks
        if checks:
            for c in checks:
                if isinstance(c, dict):
                    status = str(c.get("status", "")).lower()
                    mod = str(c.get("module", "")).lower()
                    detail = str(c.get("detail", ""))

                    if status in ["fail", "warn"]:
                        if any(k in mod for k in ["domain", "registry", "typosquat", "phish", "sebi_registry"]):
                            domain_match = re.search(r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', detail)
                            if domain_match:
                                d = self._sanitize_domain(domain_match.group(1))
                                if d:
                                    self._live_domain_counts[d] += 1

    def _sanitize_domain(self, domain_str: str) -> Optional[str]:
        """Normalize domain string into a clean hostname."""
        if not domain_str:
            return None
        d = str(domain_str).lower().strip()
        d = re.sub(r'^https?://', '', d)
        d = d.split('/')[0].split(':')[0].strip()
        if '.' in d and len(d) > 3:
            return d
        return None

    def record_seal_verification(self, is_valid: bool):
        """Record a real live PRAMAAN seal verification."""
        self._live_seals_verified += 1

    def record_seal_issued(self):
        """Record a real regulatory seal issuance."""
        self._live_seals_issued += 1

    def record_report_generated(self):
        """Record a real complaint report generated for SCORES / 1930."""
        self._live_reports_generated += 1

    async def _query_mongo_counts(self, db) -> Dict[str, Any]:
        """
        Run persistent MongoDB aggregations when database is online.
        """
        counts: Dict[str, Any] = {
            "db_scans": 0, "db_fakes": 0, "db_seals": 0, "db_reports": 0,
            "db_text": 0, "db_audio": 0, "db_video": 0, "db_image": 0,
            "db_top_domains": []
        }

        counts["db_scans"] = await db.scan_history.count_documents({})
        counts["db_fakes"] = await db.scan_history.count_documents({"verdict": "SUSPICIOUS"})
        counts["db_seals"] = await db.seal_records.count_documents({"status": "active"})
        counts["db_reports"] = await db.user_reports.count_documents({})

        counts["db_text"] = await db.scan_history.count_documents({"content_type": "text"})
        counts["db_audio"] = await db.scan_history.count_documents({"content_type": "audio"})
        counts["db_video"] = await db.scan_history.count_documents({"content_type": "video"})
        counts["db_image"] = await db.scan_history.count_documents({"content_type": "image"})

        pipeline = [
            {"$match": {"verdict": "SUSPICIOUS"}},
            {"$unwind": "$checks"},
            {"$match": {"checks.status": {"$in": ["fail", "warn"]}}},
            {"$group": {"_id": "$checks.detail", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        cursor = db.scan_history.aggregate(pipeline)
        async for doc in cursor:
            detail = doc.get("_id") or ""
            domain_match = re.search(r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', detail)
            d_name = self._sanitize_domain(domain_match.group(1)) if domain_match else self._sanitize_domain(detail.split("→")[0])
            if d_name:
                counts["db_top_domains"].append({"domain": d_name, "count": doc["count"]})
        return counts

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """
        Aggregate 100% real live system statistics combining live session
        actions and persistent MongoDB collections.
        """
        counts: Dict[str, Any] = {
            "db_scans": 0, "db_fakes": 0, "db_seals": 0, "db_reports": 0,
            "db_text": 0, "db_audio": 0, "db_video": 0, "db_image": 0,
            "db_top_domains": []
        }

        db = await get_db()
        if db is not None:
            try:
                counts = await asyncio.wait_for(self._query_mongo_counts(db), timeout=4.0)
            except asyncio.TimeoutError:
                logger.warning("MongoDB dashboard query timed out; showing real live session stats")
            except Exception as e:
                logger.warning(f"MongoDB dashboard query skipped: {e}")

        db_scans = counts["db_scans"]
        db_fakes = counts["db_fakes"]
        db_seals = counts["db_seals"]
        db_reports = counts["db_reports"]
        db_text = counts["db_text"]
        db_audio = counts["db_audio"]
        db_video = counts["db_video"]
        db_image = counts["db_image"]
        db_top_domains = counts["db_top_domains"]

        # Compute total real metrics (live session + persistent db)
        total_scans = self._live_scans + db_scans
        total_fakes = self._live_fakes + db_fakes
        total_seals = self._live_seals_verified + db_seals
        total_reports = self._live_reports_generated + db_reports

        threat_dist = {
            "text": self._live_media_counts["text"] + db_text,
            "audio": self._live_media_counts["audio"] + db_audio,
            "video": self._live_media_counts["video"] + db_video,
            "image": self._live_media_counts["image"] + db_image
        }

        # Merge live and database domain counts
        merged_domains = Counter(self._live_domain_counts)
        for item in db_top_domains:
            merged_domains[item["domain"]] += item["count"]

        top_domains_list = [
            {"domain": domain, "count": count}
            for domain, count in merged_domains.most_common(5)
        ]

        return DashboardStatsResponse(
            total_scans=total_scans,
            total_fakes_detected=total_fakes,
            total_seals_verified=total_seals,
            reports_generated=total_reports,
            top_flagged_domains=top_domains_list,
            threat_distribution=threat_dist
        )


_analytics_instance = AnalyticsService()


def get_analytics_service() -> AnalyticsService:
    return _analytics_instance


async def invalidate_dashboard_cache():
    """
    Invalidate the cached `stats:dashboard` Redis key immediately when a live
    event (scan, seal verification, report) is recorded.
    """
    try:
        from app.db.redis import get_redis

        redis = await get_redis()
        if redis is not None:
            await redis.delete("stats:dashboard")
            logger.debug("Dashboard stats cache invalidated")
    except Exception as e:
        logger.debug(f"Dashboard cache invalidation skipped: {e}")
