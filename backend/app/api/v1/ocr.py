from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from typing import Dict, Any
from app.services.ocr.ocr_service import OCRService

# --- Dependency Providers ---
def get_ocr_service() -> OCRService:
    return OCRService()

def get_medication_repository() -> list[str]:
    # Placeholder for actual SQLite Repo dependency injection
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
        "OMEPRAZOLE"
    ]
# ----------------------------

router = APIRouter(
    prefix="/ocr",
    tags=["OCR Pipeline"]
)


ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit

@router.post("/extract-drug", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def extract_drug(
    image: UploadFile = File(...),
    ocr_service: OCRService = Depends(get_ocr_service),
    known_drugs: list[str] = Depends(get_medication_repository)
):
    """
    Accepts an image file (medicine strip/box) and extracts the drug name
    using a deterministic OpenCV + Tesseract pipeline followed by 
    fuzzy database matching.
    """
    if str(image.content_type).lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed types are: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
    
    # Read the file bytes directly into memory
    # Given the 5MB limit, loading into RAM is perfectly safe and fast
    image_bytes = await image.read()
    
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the maximum limit of 5MB."
        )
        
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is completely empty."
        )

    # Call the non-blocking OCR service layer which was injected via FastAPI Depends
    try:
        raw_result = await ocr_service.extract_drug_from_image(image_bytes, known_drugs)
        
        # The API Controller assumes responsibility for framing the exact JSON envelope required
        # by the MedSync contract, protecting the Service SRP.
        return {
            "success": True,
            "data": raw_result,
            "error": None
        }
    except ValueError as val_err:
        # We classify OCR operational failures (e.g. no text found) as 400 Bad Request 
        # since the input image was likely too noisy/obscured. 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR pipeline failure: {str(e)}"
        )
    
