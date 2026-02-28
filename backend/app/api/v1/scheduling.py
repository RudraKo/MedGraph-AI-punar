from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import (
    get_cache,
    get_interaction_records,
    get_schedule_optimizer,
    rate_limit_dependency,
)
from app.core.config import get_settings
from app.infrastructure.cache.cache import CacheClient, build_cache_key
from app.services.interactions.models import InteractionRecord
from app.services.scheduling.schedule_optimizer import MedicationDosage, ScheduleOptimizer

router = APIRouter(
    prefix="/schedule",
    tags=["Scheduling Optimization"],
    dependencies=[Depends(rate_limit_dependency)],
)

settings = get_settings()


class ScheduleRequest(BaseModel):
    dosages: List[MedicationDosage]


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def generate_schedule(
    request: ScheduleRequest,
    optimizer: ScheduleOptimizer = Depends(get_schedule_optimizer),
    db_records: List[InteractionRecord] = Depends(get_interaction_records),
    cache: CacheClient = Depends(get_cache),
):
    if not request.dosages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosage list cannot be empty.",
        )

    records_payload = [row.model_dump(mode="json") for row in db_records]
    dosages_payload = [row.model_dump(mode="json") for row in request.dosages]
    cache_key = build_cache_key(
        namespace="schedule",
        payload={"dosages": dosages_payload, "records": records_payload, "v": 1},
    )

    cached_result = cache.get_json(cache_key)
    if cached_result is not None:
        return {"success": True, "data": cached_result, "error": None}

    try:
        raw_result = optimizer.generate_schedule(request.dosages, db_records)
        cache.set_json(cache_key, raw_result, ttl=settings.cache_ttl_seconds)
        return {"success": True, "data": raw_result, "error": None}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schedule optimization failure: {str(exc)}",
        )
