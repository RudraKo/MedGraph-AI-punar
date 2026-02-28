from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import (
    get_cache,
    get_interaction_engine,
    get_interaction_records,
    rate_limit_dependency,
)
from app.core.config import get_settings
from app.infrastructure.cache.cache import CacheClient, build_cache_key
from app.services.interactions.interaction_engine import InteractionEngine
from app.services.interactions.models import InteractionRecord

router = APIRouter(
    prefix="/check-interactions",
    tags=["Interaction Engine"],
    dependencies=[Depends(rate_limit_dependency)],
)

settings = get_settings()


class PrescriptionsRequest(BaseModel):
    prescribed_drugs: List[str]


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def check_interactions(
    request: PrescriptionsRequest,
    engine: InteractionEngine = Depends(get_interaction_engine),
    db_records: List[InteractionRecord] = Depends(get_interaction_records),
    cache: CacheClient = Depends(get_cache),
):
    if not request.prescribed_drugs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication list cannot be empty.",
        )

    records_payload = [row.model_dump(mode="json") for row in db_records]
    normalized_drugs = sorted({drug.strip().upper() for drug in request.prescribed_drugs if drug.strip()})
    cache_key = build_cache_key(
        namespace="interactions",
        payload={"drugs": normalized_drugs, "records": records_payload, "v": 1},
    )

    cached_result = cache.get_json(cache_key)
    if cached_result is not None:
        return {"success": True, "data": cached_result, "error": None}

    try:
        raw_result = engine.analyze_prescription(request.prescribed_drugs, db_records)
        cache.set_json(cache_key, raw_result, ttl=settings.cache_ttl_seconds)
        return {"success": True, "data": raw_result, "error": None}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interaction engine failure: {str(exc)}",
        )
