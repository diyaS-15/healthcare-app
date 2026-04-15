"""
Blood Report AI — FastAPI Backend
Deployed on Railway. All medical data is AES-256 encrypted.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging

from config import get_settings, setup_logging

# Import routers  
from routers import auth, reports, trends, chat, voice

settings = get_settings()
logger = setup_logging()

# ━━━━━━━━━━━━━━ APP INITIALIZATION ━━━━━━━━━━━━━━

app = FastAPI(
    title="Blood Report AI",
    description="AI-powered blood report analysis with end-to-end encryption",
    version=settings.app_version,
    docs_url="/api/docs" if settings.is_development else None,
    openapi_url="/api/openapi.json" if settings.is_development else None,
)

# ━━━━━━━━━━━━━━ MIDDLEWARE ━━━━━━━━━━━━━━

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━ EXCEPTION HANDLERS ━━━━━━━━━━━━━━

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# ━━━━━━━━━━━━━━ ROUTERS ━━━━━━━━━━━━━━

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(trends.router, prefix="/api/trends", tags=["Trends"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])


# ━━━━━━━━━━━━━━ HEALTH CHECK ━━━━━━━━━━━━━━

@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }

@app.get("/api/health")
async def api_health():
    return {
        "status": "ok",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


# ━━━━━━━━━━━━━━ STARTUP EVENTS ━━━━━━━━━━━━━━

@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"CORS origins: {settings.origins_list}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"🛑 Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )