from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import (
    get_medication_repository,
    get_ocr_service,
    rate_limit_dependency,
)
from app.services.ocr.ocr_service import OCRService

router = APIRouter(
    prefix="/ocr",
    tags=["OCR Pipeline"],
    dependencies=[Depends(rate_limit_dependency)],
)

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit


@router.post("/extract-drug", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def extract_drug(
    image: UploadFile = File(...),
    ocr_service: OCRService = Depends(get_ocr_service),
    known_drugs: list[str] = Depends(get_medication_repository),
):
    if str(image.content_type).lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed types are: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    image_bytes = await image.read()

    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the maximum limit of 5MB.",
        )

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is completely empty.",
        )

    try:
        raw_result = await ocr_service.extract_drug_from_image(image_bytes, known_drugs)
        return {"success": True, "data": raw_result, "error": None}
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR pipeline failure: {str(exc)}",
        )
