"""
Blood Report AI — Production Backend (Redis + Medical Core Integrated)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from config import get_settings, setup_logging

# ─────────────────────────────────────────
# 🧠 IMPORT YOUR MEDICAL ENGINE
# ─────────────────────────────────────────
from medical_core import init_db

# Routers
from routers import auth, reports, trends, chat, voice

settings = get_settings()
logger = setup_logging()

# ─────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────
app = FastAPI(
    title="Blood Report AI",
    version=settings.app_version,
    docs_url="/api/docs" if settings.is_development else None,
    openapi_url="/api/openapi.json" if settings.is_development else None,
)

# ─────────────────────────────────────────
# SECURITY HEADERS
# ─────────────────────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# ─────────────────────────────────────────
# REQUEST SIZE LIMIT
# ─────────────────────────────────────────
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    if request.headers.get("content-length"):
        if int(request.headers["content-length"]) > MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=413,
                content={"error": "Request too large"},
            )

    return await call_next(request)


# ─────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round(time.time() - start, 3)

    logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}s")

    return response


# ─────────────────────────────────────────
# CORS + HOSTS
# ─────────────────────────────────────────
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# EXCEPTION HANDLERS
# ─────────────────────────────────────────
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})


# ─────────────────────────────────────────
# ROUTERS
# ─────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth")
app.include_router(reports.router, prefix="/api/reports")
app.include_router(trends.router, prefix="/api/trends")
app.include_router(chat.router, prefix="/api/chat")
app.include_router(voice.router, prefix="/api/voice")


# ─────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────
@app.get("/")
async def health():
    return {"status": "ok", "service": "blood-report-ai"}


@app.get("/api/health")
async def api_health():
    from datetime import datetime
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.app_name}")

    if not settings.openai_api_key:
        raise RuntimeError("Missing OpenAI API key")

    # 🧠 INIT MEDICAL DATABASE
    init_db()

   # 🔥 REDIS RATE LIMITER INIT (SAFE)
    try:
        redis_conn = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
    )

        await FastAPILimiter.init(redis_conn)
        logger.info("Redis limiter enabled")

    except Exception as e:
        logger.warning(f"Redis disabled (running without rate limiting): {e}")



# ─────────────────────────────────────────
# SHUTDOWN
# ─────────────────────────────────────────
@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down application")


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
    )