import asyncio
from app.services.ocr.ocr_service import OCRService

async def test_ocr_pipeline():
    # 1. Provide exact match strings simulating the SQL DB Repository layer
    known_database = [
        "ASPIRIN", 
        "WARFARIN", 
        "METFORMIN", 
        "AMOXICILLIN", 
        "LISINOPRIL"
    ]
    
    # 2. Load the intentionally noisy image with a typo "WARFARN"
    with open("backend/test_rotated.png", "rb") as image_file:
        image_bytes = image_file.read()
        print(f"File loaded successfully: {len(image_bytes)} bytes")
    
    ocr_service = OCRService()
    
    # 3. Process utilizing the async facade (no-block constraint)
    result = await ocr_service.extract_drug_from_image(image_bytes, known_database)
    
    import json
    print("\nExtraction Result Envelope:")
    # 4. Assert against the strict MedSync REST Contract
    print("API Response Envelope:")
    print(json.dumps(result, indent=2))
    
    # Final assertion testing framework bounds
    assert result["matched_drug"] == "WARFARIN"
    print("\n✅ Non-blocking OCR pipeline executed successfully.")

if __name__ == "__main__":
    asyncio.run(test_ocr_pipeline())
