"""
ReliefSync-AI — FastAPI Application Entry Point.
AI-powered crisis response and volunteer coordination platform.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time

from .core.config import get_settings
from .core.security import rate_limit_middleware
from .models.schemas import HealthCheck
from .routers import emergencies, volunteers, tasks, analytics

# ── Structured Logging ──────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
)
logger = structlog.get_logger(__name__)

# ── App Factory ─────────────────────────────────────────────────
settings = get_settings()

app = FastAPI(
    title="ReliefSync-AI API",
    description=(
        "AI-powered crisis response and volunteer coordination platform. "
        "Uses Google Gemini for severity prediction, volunteer matching, "
        "resource forecasting, fraud detection, and multilingual communication."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Logging & Rate Limiting Middleware ──────────────────
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start_time = time.time()
    # Rate limiting
    try:
        await rate_limit_middleware(request)
    except Exception as exc:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 1)
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration,
    )
    response.headers["X-Response-Time"] = f"{duration}ms"
    return response


# ── Routers ─────────────────────────────────────────────────────
app.include_router(emergencies.router, prefix=settings.API_PREFIX)
app.include_router(volunteers.router, prefix=settings.API_PREFIX)
app.include_router(tasks.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)


# ── Health Check ────────────────────────────────────────────────
@app.get("/health", response_model=HealthCheck, tags=["System"])
async def health_check():
    """System health check endpoint for load balancers and monitoring."""
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services={
            "supabase": "connected" if settings.SUPABASE_URL else "not_configured",
            "gemini_ai": "configured" if settings.GEMINI_API_KEY else "not_configured",
            "google_maps": "configured" if settings.GOOGLE_MAPS_API_KEY else "not_configured",
        },
    )


@app.get("/", tags=["System"])
async def root():
    """API root — provides service info and links."""
    return {
        "service": "ReliefSync-AI",
        "version": settings.APP_VERSION,
        "description": "AI-powered crisis response and volunteer coordination",
        "docs": "/docs",
        "health": "/health",
        "api_prefix": settings.API_PREFIX,
        "google_services": [
            "Gemini 2.0 Flash (AI predictions)",
            "Cloud Firestore (database)",
            "Firebase Auth (authentication)",
            "Google Maps (geolocation & routing)",
            "Cloud Vision AI (image analysis)",
            "Cloud Speech-to-Text (voice reports)",
            "Cloud Translation (multilingual)",
            "BigQuery (analytics pipeline)",
            "Cloud Run (deployment)",
        ],
    }
