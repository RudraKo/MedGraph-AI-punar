from __future__ import annotations

import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import interactions, jobs, ocr, scheduling
from app.core.config import get_settings
from app.infrastructure.cache.cache import get_cache_client
from app.infrastructure.db.database import check_database_health, init_database
from app.workers.celery_app import celery_app

settings = get_settings()


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["default"],
                "level": settings.log_level,
            },
        }
    )


configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="A graph-based polypharmacy safety and medication coordination platform.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ocr.router, prefix="/api/v1")
app.include_router(interactions.router, prefix="/api/v1")
app.include_router(scheduling.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event() -> None:
    init_database()
    logger.info("Application startup complete")


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/health/live", tags=["System"])
async def liveness_check():
    return {"status": "alive"}


@app.get("/health/ready", tags=["System"])
async def readiness_check():
    db_ok = check_database_health()
    cache_ok = get_cache_client().ping()

    if celery_app is None:
        queue_ok = False
        queue_mode = "disabled"
    else:
        try:
            # Fast broker-level check without dispatching tasks.
            with celery_app.connection_for_read() as conn:
                conn.ensure_connection(max_retries=1)
            queue_ok = True
            queue_mode = "enabled"
        except Exception:
            queue_ok = False
            queue_mode = "enabled"

    overall = db_ok and cache_ok and (queue_ok or queue_mode == "disabled")
    return {
        "status": "ready" if overall else "degraded",
        "dependencies": {
            "database": db_ok,
            "cache": cache_ok,
            "queue": queue_ok,
            "queue_mode": queue_mode,
        },
    }
