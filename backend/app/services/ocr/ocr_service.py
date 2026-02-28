import asyncio
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

import pytesseract
import cv2

from .image_processor import ImageProcessor
from .text_cleaner import TextCleaner
from .drug_matcher import DrugMatcher

class OCRService:
    """
    Orchestrates the OpenCV preprocessing, Tesseract extraction,
    and RapidFuzz matching entirely off the main event loop.
    Returns the required REST API JSON envelope.
    """

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
            raw_text = pytesseract.image_to_string(processed_img, config='--psm 6')

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
