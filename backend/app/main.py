"""
PRAMAAN-SHIELD — FastAPI Application Entry Point (Refreshed)
File: backend/app/main.py
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.utils.logger import configure_logger
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis import connect_to_redis, close_redis_connection

from app.routers import scan, verify, seal, report, dashboard, webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logger()
    logger.info("PRAMAAN-SHIELD backend starting up...")

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

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://pramaan-shield.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Simple rate limit check on /api/ endpoints via client IP."""
    if request.url.path.startswith("/api/"):
        client_ip = request.client.host if request.client else "127.0.0.1"
        try:
            from app.db.redis import get_redis
            redis = await get_redis()
            key = f"rate_limit:{client_ip}"
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, 60)
            if current > 60:  # 60 reqs per minute
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={"error": True, "message": "Rate limit exceeded (60 requests/min). Please try again later."}
                )
        except Exception:
            pass  # Fail-open if Redis unavailable
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
    ai_status = "live" if scan.gemini_svc.available and not getattr(scan.gemini_svc, "degraded", False) else "degraded"
    return {
        "status": "ok",
        "version": "1.0.0",
        "phase": "2 — Detection & Authentication Active",
        "service": "PRAMAAN-SHIELD",
        "ai_layer": ai_status
    }


@app.get("/", tags=["system"])
async def root():
    return {
        "message": "PRAMAAN-SHIELD API — प्रमाण शील्ड",
        "docs": "/docs",
        "health": "/health"
    }
