import asyncio
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

import pytesseract
import cv2

from app.core.config import get_settings
from .image_processor import ImageProcessor
from .text_cleaner import TextCleaner
from .drug_matcher import DrugMatcher


def get_ocr_runtime_status() -> Dict[str, Any]:
    settings = get_settings()
    configured_cmd = settings.tesseract_cmd or pytesseract.pytesseract.tesseract_cmd
    requested_langs = [lang for lang in settings.ocr_language.split("+") if lang]

    status: Dict[str, Any] = {
        "ready": False,
        "configured_tesseract_cmd": configured_cmd or None,
        "ocr_language": settings.ocr_language,
        "version": None,
        "available_languages": [],
        "missing_languages": [],
        "message": "",
    }

    try:
        status["version"] = str(pytesseract.get_tesseract_version())
    except Exception as exc:
        status["message"] = f"Tesseract binary unavailable: {exc}"
        return status

    try:
        available_languages = pytesseract.get_languages(config="")
        status["available_languages"] = available_languages
    except Exception as exc:
        status["message"] = f"Tesseract found, but language data check failed: {exc}"
        return status

    missing_languages = [
        language for language in requested_langs if language not in status["available_languages"]
    ]
    status["missing_languages"] = missing_languages
    status["ready"] = len(missing_languages) == 0

    if status["ready"]:
        status["message"] = "OCR runtime is ready."
    else:
        status["message"] = (
            "Tesseract is installed, but requested OCR languages are missing: "
            + ",".join(missing_languages)
        )

    return status


class OCRService:
    """
    Orchestrates the OpenCV preprocessing, Tesseract extraction,
    and RapidFuzz matching entirely off the main event loop.
    Returns the required REST API JSON envelope.
    """
    def __init__(self) -> None:
        settings = get_settings()
        self._ocr_language = settings.ocr_language
        if settings.tesseract_cmd:
            # Honor explicit binary path from env (useful on macOS/Homebrew).
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    def _execute_sync_pipeline(self, image_bytes: bytes, known_drugs: List[str]) -> Dict[str, Any]:
        """
        The heavy lifting pipeline designed to run in a separate thread.
        This contains NO database logic (SqlAlchemy sessions) and relies
        entirely on the provided `known_drugs` list.
        """
        try:
            # 1. Image Preprocessing (OpenCV)
            processed_img = ImageProcessor.preprocess_for_ocr(image_bytes)

            # 2. Extract Text (Tesseract)
            # PSM 6 assumes a single uniform block of text (ideal for medicine boxes)
            raw_text = pytesseract.image_to_string(
                processed_img,
                config="--psm 6",
                lang=self._ocr_language,
            )

            if not raw_text.strip():
                 raise ValueError("No recognizable text found in the image.")

            # 3. Clean and sanitize the string
            clean_text = TextCleaner.clean_ocr_text(raw_text)

            # 4. Fuzzy Match against the known drugs array
            match_result = DrugMatcher.match_drug(clean_text, known_drugs)

            if not match_result:
                 raise ValueError(f"Extracted text '{clean_text}' did not confidently match any known drugs.")

            drug_name, confidence = match_result

            # Return raw Domain details (SRP - Let the router handle HTTP Envelope wrapping)
            return {
                "extracted_text": clean_text,
                "matched_drug": drug_name,
                "confidence_score": confidence
            }

        except ValueError as val_err:
             # Captured from ImageProcessor format exceptions
             raise val_err
        except Exception as e:
             # Catch-all for Tesseract binary path failures, memory faults, etc.
             raise RuntimeError(f"OCR pipeline failure: {str(e)}")

    async def extract_drug_from_image(self, image_bytes: bytes, known_drugs: List[str]) -> Dict[str, Any]:
        """
        Asynchronous facade utilizing asyncio.to_thread()
        to prevent blocking the Uvicorn/FastAPI event loop.
        
        Args:
            image_bytes (bytes): The raw file bytes uploaded by the frontend.
            known_drugs (List[str]): Extracted from the Domain/Repository layer 
                                     prior to calling this service.
        """
        # Execute the CPU-bound OpenCV and Tesseract processing in a separate thread
        result = await asyncio.to_thread(self._execute_sync_pipeline, image_bytes, known_drugs)
        return result
