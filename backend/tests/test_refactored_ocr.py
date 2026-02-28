import asyncio
import json
from app.services.ocr.image_processor import ImageProcessor
from app.services.ocr.text_cleaner import TextCleaner
from app.services.ocr.drug_matcher import DrugMatcher

async def test_ocr_pipeline():
    known_database = [
        "ASPIRIN", 
        "WARFARIN", 
        "METFORMIN", 
        "AMOXICILLIN", 
        "LISINOPRIL"
    ]
    
    with open("backend/test_rotated.png", "rb") as image_file:
        image_bytes = image_file.read()
        
    print("Testing ImageProcessor (Auto-Rotation, CLAHE, Contour Crop)...")
    try:
        processed_img = ImageProcessor.preprocess_for_ocr(image_bytes)
        print("✅ OpenCV Preprocessing pipeline executed without crashing.")
        import cv2
        cv2.imwrite("backend/test_output_processed.png", processed_img)
        print("✅ Saved output to 'backend/test_output_processed.png' for visual verification.")
    except Exception as e:
        print(f"❌ OpenCV Error: {e}")
        return

    print("\nTesting TextCleaner & DrugMatcher (Mocking Tesseract output)...")
    
    # Mock Tesseract extracting text from the perfectly rotated and thresholded box
    mock_tesseract_output = "AM0XIC1LL1N 500 MG\n" 
    
    clean_text = TextCleaner.clean_ocr_text(mock_tesseract_output)
    match_result = DrugMatcher.match_drug(clean_text, known_database)
    
    assert match_result is not None
    drug_name, confidence = match_result
    
    print("\nAPI Response Envelope (Simulation):")
    print(json.dumps({
        "success": True,
        "data": {
            "extracted_text": clean_text,
            "matched_drug": drug_name,
            "confidence_score": confidence
        },
        "error": None
    }, indent=2))
    
    assert drug_name == "AMOXICILLIN"
    print("\n✅ Multi-stage Robust OCR logic executed successfully.")

if __name__ == "__main__":
    asyncio.run(test_ocr_pipeline())
