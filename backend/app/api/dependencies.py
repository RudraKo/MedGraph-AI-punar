from __future__ import annotations

import time
from typing import List

from fastapi import Depends, HTTPException, Request, status

from app.core.config import get_settings
from app.infrastructure.cache.cache import CacheClient, get_cache_client
from app.infrastructure.db.database import get_db
from app.services.interactions.interaction_engine import InteractionEngine
from app.services.interactions.models import InteractionRecord, SeverityLevel
from app.services.ocr.ocr_service import OCRService
from app.services.scheduling.schedule_optimizer import ScheduleOptimizer


def get_ocr_service() -> OCRService:
    return OCRService()


def get_interaction_engine() -> InteractionEngine:
    return InteractionEngine()


def get_schedule_optimizer() -> ScheduleOptimizer:
    return ScheduleOptimizer()


def get_cache() -> CacheClient:
    return get_cache_client()


def get_medication_repository() -> list[str]:
    # Placeholder for repository-backed drug lookup.
    return [
        "ASPIRIN",
        "WARFARIN",
        "METFORMIN",
        "AMOXICILLIN",
        "LISINOPRIL",
        "PARACETAMOL",
        "IBUPROFEN",
        "ATORVASTATIN",
        "AMLOGIPINE",
        "OMEPRAZOLE",
    ]


def get_interaction_records() -> List[InteractionRecord]:
    # Placeholder for DB-backed interaction fetch.
    return [
        InteractionRecord(
            drug_a="ASPIRIN",
            drug_b="WARFARIN",
            severity=SeverityLevel.SEVERE,
            explanation="Increased bleeding risk.",
        ),
        InteractionRecord(
            drug_a="OMEPRAZOLE",
            drug_b="WARFARIN",
            severity=SeverityLevel.MODERATE,
            explanation="Altered metabolism.",
        ),
    ]


def rate_limit_dependency(
    request: Request,
    cache: CacheClient = Depends(get_cache),
) -> None:
    settings = get_settings()

    if not settings.rate_limit_enabled:
        return

    if request.url.path in {"/health", "/health/live", "/health/ready"}:
        return

    client_ip = request.client.host if request.client else "unknown"
    bucket = int(time.time() // 60)
    key = f"rate-limit:{client_ip}:{request.url.path}:{bucket}"

    current_count = cache.increment(key, ttl=70)
    if current_count > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please retry in 1 minute.",
        )


__all__ = [
    "get_db",
    "get_cache",
    "get_ocr_service",
    "get_interaction_engine",
    "get_schedule_optimizer",
    "get_medication_repository",
    "get_interaction_records",
    "rate_limit_dependency",
]
