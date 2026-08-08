"""
PRAMAAN-SHIELD — FastAPI Application Entry Point (Refreshed)
File: backend/app/main.py
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.utils.logger import configure_logger
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis import connect_to_redis, close_redis_connection
from app.utils.file_cleanup import cleanup_all_temp_files

from app.routers import scan, verify, seal, report, dashboard, webhook

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logger()
    logger.info("PRAMAAN-SHIELD backend starting up...")
    cleanup_all_temp_files()

    # Connect DB & Redis on lifespan startup
    try:
        await connect_to_mongo()
        await connect_to_redis()
    except Exception as e:
        logger.warning(f"Database connection during startup failed (will retry on requests): {e}")

    logger.info("Startup complete — All routers active")
    yield
    logger.info("PRAMAAN-SHIELD backend shutting down...")
    try:
        await close_mongo_connection()
        await close_redis_connection()
    except Exception as e:
        logger.warning(f"Error during shutdown cleanup: {e}")


app = FastAPI(
    title="PRAMAAN-SHIELD API",
    description=(
        "Three-pillar trust engine for SEBI TechSprint 2026: "
        "Detection · Authentication · Redressal"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

ALLOWED_ORIGINS = settings.resolved_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request, call_next):
    """Add production security response headers per OWASP guidelines."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' http://localhost:8000"
    )
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


ROUTE_LIMITS = {
    "/api/scan": {"limit": 15, "window": 60},      # 15 scans/min (heavy compute)
    "/api/report": {"limit": 20, "window": 60},    # 20 reports/min
    "/api/report/": {"limit": 40, "window": 60},   # evidence PDF download (route template, not per-ID)
    "/api/verify": {"limit": 40, "window": 60},    # 40 verify/min
    "/api/seal/sign": {"limit": 10, "window": 60}, # 10 seal signs/min
}
DEFAULT_LIMIT = {"limit": 60, "window": 60}


import time
import ipaddress
from collections import OrderedDict

# Bounded in-memory rate-limit fallback. Used only while Redis is offline.
# OrderedDict so we can evict oldest entries and stop unbounded growth under
# a distributed IP sweep. Each entry: key -> (window_start, hits).
FALLBACK_LIMITS: "OrderedDict[str, tuple[float, int]]" = OrderedDict()
FALLBACK_LIMITS_MAX = 10_000


def _bucket_for(request) -> str:
    """Rate-limit bucket key: route TEMPLATE (not concrete path) so per-ID URLs
    like /api/report/<uuid>/pdf share one bucket instead of each getting a fresh
    limit (which allowed unlimited PDF CPU burn)."""
    route = getattr(request.scope.get("route"), "path", None)
    if route:
        return route
    # Before routing completes (or in tests), fall back to a normalized prefix.
    path = request.url.path
    parts = path.split("/")
    if len(parts) >= 5 and parts[1] == "api" and parts[2] == "report":
        return "/api/report/"
    return path


def _client_ip(request) -> str:
    """Resolve the effective client IP.

    Security: X-Forwarded-For is honoured ONLY when the immediate TCP peer is
    one of our own proxies (settings.TRUSTED_PROXY_CIDRS). With no proxies
    configured, we return request.client.host — remote spoofing of XFF is
    impossible because the header is simply ignored."""
    peer = request.client.host if request.client else "127.0.0.1"
    try:
        trusted = settings.trusted_proxy_cidrs()
        if trusted:
            peer_addr = ipaddress.ip_address(peer)
            if any(peer_addr in net for net in trusted):
                forwarded = request.headers.get("x-forwarded-for", "")
                if forwarded:
                    # Right-most entry is the one added by our own proxy chain.
                    return forwarded.split(",")[-1].strip() or peer
    except (ValueError, TypeError):
        pass
    return peer


def _fallback_bump(ip_key: str, window: int, now: float) -> int:
    """Increment the per-ip:path hit counter, keeping the map bounded."""
    if len(FALLBACK_LIMITS) >= FALLBACK_LIMITS_MAX:
        # Evict the oldest entry; if it is still inside its window, re-insert it
        # under its OWN key (MRU position) so live buckets are never dropped or
        # mixed up with the current request's bucket.
        while len(FALLBACK_LIMITS) >= FALLBACK_LIMITS_MAX:
            k, (start, hits) = FALLBACK_LIMITS.popitem(last=False)
            if now - start <= window:            # still live — keep it
                FALLBACK_LIMITS[k] = (start, hits)
                FALLBACK_LIMITS.move_to_end(k)
            # expired entries are dropped; loop exits after one eviction round
            break

    window_start, hits = FALLBACK_LIMITS.get(ip_key, (0, 0))
    if now - window_start > window:
        window_start, hits = now, 0
    hits += 1
    FALLBACK_LIMITS[ip_key] = (window_start, hits)
    FALLBACK_LIMITS.move_to_end(ip_key)
    return hits


@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Per-endpoint Redis rate limit check via client IP with local fail-safe fallback."""
    if request.url.path.startswith("/api/"):
        client_ip = _client_ip(request)
        if client_ip in ("127.0.0.1", "::1", "localhost"):
            return await call_next(request)
        path = _bucket_for(request)
        config = ROUTE_LIMITS.get(path, DEFAULT_LIMIT)
        use_fallback = False
        try:
            from app.db.redis import get_redis
            redis = await get_redis()
            if redis:
                key = f"rate_limit:{path}:{client_ip}"
                current = await redis.incr(key)
                if current == 1:
                    await redis.expire(key, config["window"])
                if current > config["limit"]:
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": True,
                            "message": f"Rate limit exceeded for {path} ({config['limit']} requests/{config['window']}s). Please try again later."
                        }
                    )
            else:
                use_fallback = True
        except Exception as e:
            logger.warning(f"Redis rate limiter offline ({e}). Falling back to in-memory protection.")
            use_fallback = True

        if use_fallback:
            now = time.time()
            ip_key = f"{client_ip}:{path}"
            hits = _fallback_bump(ip_key, config["window"], now)
            if hits > config["limit"]:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": True,
                        "message": f"Rate limit exceeded for {path} ({config['limit']} requests/{config['window']}s). Local fallback active."
                    }
                )
    response = await call_next(request)
    return response

# Register Routers
app.include_router(scan.router, prefix="/api")
app.include_router(verify.router, prefix="/api")
app.include_router(seal.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")


@app.get("/health", tags=["system"])
async def health_check():
    # Lightweight liveness only. Internal AI-layer state (Gemini availability,
    # model modes, ML backend names) is NOT exposed here — see /healthz for a
    # versioned, auth-gated ops view.
    return {
        "status": "ok",
        "version": "1.0.0",
        "phase": "2 — Detection & Authentication Active",
        "service": "PRAMAAN-SHIELD",
    }


@app.get("/", tags=["system"])
async def root():
    return {
        "message": "PRAMAAN-SHIELD API — प्रमाण शील्ड",
        "docs": "/docs",
        "health": "/health"
    }
