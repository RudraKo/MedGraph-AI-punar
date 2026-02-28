from __future__ import annotations

import base64
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.api.dependencies import (
    get_interaction_records,
    get_medication_repository,
    rate_limit_dependency,
)
from app.services.interactions.models import InteractionRecord
from app.services.scheduling.schedule_optimizer import MedicationDosage
from app.workers.celery_app import celery_app
from app.workers.tasks import (
    analyze_interactions_task,
    extract_drug_task,
    generate_schedule_task,
)

try:
    from celery.result import AsyncResult
except ImportError:  # pragma: no cover - optional dependency fallback
    AsyncResult = None


router = APIRouter(
    prefix="/jobs",
    tags=["Async Jobs"],
    dependencies=[Depends(rate_limit_dependency)],
)

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class PrescriptionsRequest(BaseModel):
    prescribed_drugs: List[str]


class ScheduleRequest(BaseModel):
    dosages: List[MedicationDosage]


class JobAcceptedResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: str | None


def _ensure_job_backend_available() -> None:
    if celery_app is None or AsyncResult is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Async job system is unavailable. Configure Celery + Redis.",
        )
    try:
        with celery_app.connection_for_write() as conn:
            conn.ensure_connection(max_retries=1)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Async job backend is unreachable: {str(exc)}",
        ) from exc


@router.post(
    "/ocr/extract-drug",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_ocr_job(
    image: UploadFile = File(...),
    known_drugs: list[str] = Depends(get_medication_repository),
) -> Dict[str, Any]:
    _ensure_job_backend_available()

    if str(image.content_type).lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    image_bytes = await image.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 5 MB.",
        )
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    try:
        task = extract_drug_task.delay(encoded_image, known_drugs)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to enqueue OCR job: {str(exc)}",
        ) from exc

    return {
        "success": True,
        "data": {"job_id": task.id, "status": "PENDING", "job_type": "ocr"},
        "error": None,
    }


@router.post(
    "/interactions/check",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_interactions_job(
    request: PrescriptionsRequest,
    db_records: List[InteractionRecord] = Depends(get_interaction_records),
) -> Dict[str, Any]:
    _ensure_job_backend_available()

    if not request.prescribed_drugs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication list cannot be empty.",
        )

    records_payload = [row.model_dump(mode="json") for row in db_records]
    try:
        task = analyze_interactions_task.delay(request.prescribed_drugs, records_payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to enqueue interaction job: {str(exc)}",
        ) from exc

    return {
        "success": True,
        "data": {
            "job_id": task.id,
            "status": "PENDING",
            "job_type": "interactions",
        },
        "error": None,
    }


@router.post(
    "/schedule/generate",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_schedule_job(
    request: ScheduleRequest,
    db_records: List[InteractionRecord] = Depends(get_interaction_records),
) -> Dict[str, Any]:
    _ensure_job_backend_available()

    if not request.dosages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosage list cannot be empty.",
        )

    dosages_payload = [row.model_dump(mode="json") for row in request.dosages]
    records_payload = [row.model_dump(mode="json") for row in db_records]

    try:
        task = generate_schedule_task.delay(dosages_payload, records_payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to enqueue schedule job: {str(exc)}",
        ) from exc

    return {
        "success": True,
        "data": {"job_id": task.id, "status": "PENDING", "job_type": "schedule"},
        "error": None,
    }


@router.get("/{job_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def get_job_status(job_id: str) -> Dict[str, Any]:
    _ensure_job_backend_available()

    result = AsyncResult(job_id, app=celery_app)

    payload: Dict[str, Any] = {
        "job_id": job_id,
        "status": result.status,
        "ready": result.ready(),
    }

    if result.status == "SUCCESS":
        payload["result"] = result.result
    elif result.status == "FAILURE":
        payload["error"] = str(result.result)

    return {"success": True, "data": payload, "error": None}
